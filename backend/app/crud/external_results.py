"""CRUD operations for External Run Sessions (BGSTM#300)."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.external_results import ExternalRunSession, RunStatus
from app.models.project import Project
from app.schemas.external_results import SessionCreate, SessionFinish

# Terminal statuses — no further transitions allowed once reached.
_TERMINAL_STATUSES = {RunStatus.passed, RunStatus.failed, RunStatus.aborted}

# Idempotency window in seconds: duplicate session creates within this window
# (same project_id, runner, ci_url, git_sha) return the existing session.
_IDEMPOTENCY_WINDOW_SECONDS = 60


async def create_session(
    db: AsyncSession,
    *,
    payload: SessionCreate,
    runner_token_id: UUID,
) -> ExternalRunSession:
    """Create a new ExternalRunSession, honouring the idempotency window.

    If an active (started) session with the same (project_id, runner, ci_url,
    git_sha) was created within the last ``_IDEMPOTENCY_WINDOW_SECONDS``
    seconds by the same runner token, the existing session is returned instead
    of creating a duplicate.

    """
    project_result = await db.execute(select(Project.id).where(Project.id == payload.project_id))
    project_id = project_result.scalar_one_or_none()
    if project_id is None:
        raise ValueError(
            {
                "code": "session.project_not_found",
                "message": f"Project {payload.project_id} does not exist.",
                "details": None,
            }
        )

    cutoff = datetime.now(tz=timezone.utc).replace(tzinfo=None) - timedelta(seconds=_IDEMPOTENCY_WINDOW_SECONDS)

    # Normalise ci_url to a plain string so we can compare it.
    ci_url_str = str(payload.ci_url) if payload.ci_url is not None else None

    stmt = (
        select(ExternalRunSession)
        .where(ExternalRunSession.project_id == payload.project_id)
        .where(ExternalRunSession.runner == payload.runner)
        .where(ExternalRunSession.created_by_runner_token_id == runner_token_id)
        .where(ExternalRunSession.status == RunStatus.started)
        .where(ExternalRunSession.started_at >= cutoff)
    )
    if ci_url_str is not None:
        stmt = stmt.where(ExternalRunSession.ci_url == ci_url_str)
    else:
        stmt = stmt.where(ExternalRunSession.ci_url.is_(None))

    if payload.git_sha is not None:
        stmt = stmt.where(ExternalRunSession.git_sha == payload.git_sha)
    else:
        stmt = stmt.where(ExternalRunSession.git_sha.is_(None))

    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing is not None:
        return existing

    session = ExternalRunSession(
        project_id=payload.project_id,
        runner=payload.runner,
        status=RunStatus.started,
        git_sha=payload.git_sha,
        git_branch=payload.git_branch,
        ci_url=ci_url_str,
        run_metadata=payload.metadata,
        started_at=datetime.now(tz=timezone.utc).replace(tzinfo=None),
        created_by_runner_token_id=runner_token_id,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def finish_session_db(
    db: AsyncSession,
    *,
    session_id: UUID,
    payload: SessionFinish,
) -> ExternalRunSession | None:
    """Apply the finish payload to the session and return the updated model.

    Returns ``None`` if the session does not exist.

    Raises ``ValueError`` with a structured dict payload on transition
    violations so the API layer can return the appropriate 409.

    """
    result = await db.execute(select(ExternalRunSession).where(ExternalRunSession.id == session_id))
    session = result.scalar_one_or_none()
    if session is None:
        return None

    current = RunStatus(session.status)

    # All terminal statuses block further transitions.
    if current in _TERMINAL_STATUSES:
        raise ValueError(
            {
                "code": "session.transition.invalid",
                "message": (
                    f"Cannot transition session from '{current.value}' to '{payload.status.value}': "
                    f"session is already in a terminal state."
                ),
                "details": {"current_status": current.value, "requested_status": payload.status.value},
            }
        )

    session.status = payload.status
    session.summary = payload.summary
    session.finished_at = datetime.now(tz=timezone.utc).replace(tzinfo=None)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(
    db: AsyncSession,
    session_id: UUID,
) -> ExternalRunSession | None:
    """Return a single ExternalRunSession by primary key, or None."""
    result = await db.execute(select(ExternalRunSession).where(ExternalRunSession.id == session_id))
    return result.scalar_one_or_none()
