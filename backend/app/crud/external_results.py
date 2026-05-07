"""CRUD operations for External Results entities."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.external_results import CaseOutcome, ExternalCaseResult, ExternalRunSession, RunStatus
from app.models.link import LinkSource, RequirementTestCaseLink
from app.models.requirement import PriorityLevel, Requirement
from app.models.test_case import AutomationStatus, TestCase, TestCaseType
from app.schemas.external_results import CaseResultCreate, CaseResultUpdate, SessionCreate, SessionFinish

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

    # TODO(#297): Write audit entry ``external_results.session.start`` here.
    """
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

    # TODO(#297): Write audit entry ``external_results.session.finish`` here.
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


async def get_requirement_ids_for_test_case(db: AsyncSession, *, test_case_id: UUID | None) -> list[UUID]:
    """Return linked requirement IDs for a test case."""
    if test_case_id is None:
        return []
    result = await db.execute(
        select(RequirementTestCaseLink.requirement_id).where(RequirementTestCaseLink.test_case_id == test_case_id)
    )
    return list(result.scalars().all())


async def _link_requirements_to_test_case(
    db: AsyncSession,
    *,
    test_case_id: UUID,
    requirement_ids: list[UUID],
) -> None:
    if not requirement_ids:
        return

    req_result = await db.execute(select(Requirement.id).where(Requirement.id.in_(requirement_ids)))
    existing_requirements = set(req_result.scalars().all())
    missing_requirement_ids = [req_id for req_id in requirement_ids if req_id not in existing_requirements]
    if missing_requirement_ids:
        raise ValueError(
            {
                "code": "requirement.not_found",
                "message": "One or more requirement_ids do not exist.",
                "details": {"missing_requirement_ids": [str(req_id) for req_id in missing_requirement_ids]},
            }
        )

    existing_link_result = await db.execute(
        select(RequirementTestCaseLink.requirement_id)
        .where(RequirementTestCaseLink.test_case_id == test_case_id)
        .where(RequirementTestCaseLink.requirement_id.in_(requirement_ids))
    )
    existing_link_ids = set(existing_link_result.scalars().all())

    for req_id in requirement_ids:
        if req_id in existing_link_ids:
            continue
        db.add(
            RequirementTestCaseLink(
                requirement_id=req_id,
                test_case_id=test_case_id,
                link_source=LinkSource.IMPORTED,
            )
        )


async def create_case_result(
    db: AsyncSession,
    *,
    payload: CaseResultCreate,
) -> tuple[ExternalCaseResult, bool, bool]:
    """Create a case result with test-case auto-upsert and idempotency."""
    session_result = await db.execute(select(ExternalRunSession).where(ExternalRunSession.id == payload.session_id))
    session = session_result.scalar_one_or_none()
    if session is None:
        raise ValueError(
            {
                "code": "session.not_found",
                "message": f"Session {payload.session_id} does not exist.",
                "details": None,
            }
        )

    if RunStatus(session.status) != RunStatus.started:
        raise ValueError(
            {
                "code": "session.already_finished",
                "message": (
                    f"Cannot add case results to session {payload.session_id} in status '{session.status.value}'."
                ),
                "details": {"status": session.status.value},
            }
        )

    if payload.test_case_id is None and payload.external_id is None:
        raise ValueError(
            {
                "code": "missing_identifier",
                "message": "At least one of 'test_case_id' or 'external_id' must be provided.",
                "details": None,
            }
        )

    if payload.external_id is not None:
        existing_result_q = await db.execute(
            select(ExternalCaseResult)
            .where(ExternalCaseResult.session_id == payload.session_id)
            .where(ExternalCaseResult.external_id == payload.external_id)
        )
        existing_result = existing_result_q.scalar_one_or_none()
        if existing_result is not None:
            if payload.requirement_ids and existing_result.test_case_id is not None:
                await _link_requirements_to_test_case(
                    db,
                    test_case_id=existing_result.test_case_id,
                    requirement_ids=payload.requirement_ids,
                )
                await db.commit()
                await db.refresh(existing_result)
            return existing_result, False, False

    auto_registered = False
    linked_test_case: TestCase | None = None

    if payload.test_case_id is not None:
        tc_result = await db.execute(select(TestCase).where(TestCase.id == payload.test_case_id))
        linked_test_case = tc_result.scalar_one_or_none()
        if linked_test_case is None:
            raise LookupError(
                {
                    "code": "test_case_not_found",
                    "message": f"Test case {payload.test_case_id} does not exist.",
                    "details": None,
                }
            )
    elif payload.external_id is not None:
        tc_result = await db.execute(select(TestCase).where(TestCase.external_id == payload.external_id))
        linked_test_case = tc_result.scalar_one_or_none()
        if linked_test_case is None:
            linked_test_case = TestCase(
                external_id=payload.external_id,
                title=payload.title,
                description=f"Auto-registered from external result '{payload.external_id}'.",
                type=TestCaseType.FUNCTIONAL,
                priority=PriorityLevel.MEDIUM,
                automation_status=AutomationStatus.AUTOMATED,
                auto_registered=True,
            )
            db.add(linked_test_case)
            await db.flush()
            auto_registered = True

    case_result = ExternalCaseResult(
        session_id=payload.session_id,
        project_id=session.project_id,
        test_case_id=linked_test_case.id if linked_test_case is not None else None,
        external_id=payload.external_id,
        title=payload.title,
        outcome=CaseOutcome(payload.outcome.value),
        duration_ms=payload.duration_ms,
        error_message=payload.error_message,
    )
    db.add(case_result)
    await db.flush()

    if payload.requirement_ids and case_result.test_case_id is not None:
        await _link_requirements_to_test_case(
            db,
            test_case_id=case_result.test_case_id,
            requirement_ids=payload.requirement_ids,
        )

    await db.commit()
    await db.refresh(case_result)
    return case_result, True, auto_registered


async def update_case_result(
    db: AsyncSession,
    *,
    case_result_id: UUID,
    payload: CaseResultUpdate,
) -> ExternalCaseResult | None:
    """Update a case result, enforcing outcome transition rules."""
    result = await db.execute(select(ExternalCaseResult).where(ExternalCaseResult.id == case_result_id))
    case_result = result.scalar_one_or_none()
    if case_result is None:
        return None

    if payload.outcome is not None:
        current = CaseOutcome(case_result.outcome)
        requested = CaseOutcome(payload.outcome.value)
        transition_allowed = requested == current or (
            current in {CaseOutcome.passed, CaseOutcome.failed, CaseOutcome.skipped} and requested == CaseOutcome.flaky
        )
        if not transition_allowed:
            raise ValueError(
                {
                    "code": "invalid_status_transition",
                    "message": (
                        f"Invalid case-result status transition from '{current.value}' to '{requested.value}'."
                    ),
                    "details": {"current_status": current.value, "requested_status": requested.value},
                }
            )
        case_result.outcome = requested

    if payload.duration_ms is not None:
        case_result.duration_ms = payload.duration_ms
    if payload.error_message is not None:
        case_result.error_message = payload.error_message

    await db.commit()
    await db.refresh(case_result)
    return case_result


async def get_case_result(
    db: AsyncSession,
    case_result_id: UUID,
) -> ExternalCaseResult | None:
    """Return a single case result by primary key, or None."""
    result = await db.execute(select(ExternalCaseResult).where(ExternalCaseResult.id == case_result_id))
    return result.scalar_one_or_none()
