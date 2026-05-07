"""API router for External Results — session endpoints (BGSTM#300).

Implements:
  POST   /external-results/session          – start a run (201 Created)
  PATCH  /external-results/session/{id}     – finish a run
  GET    /external-results/session/{id}     – read a session (runner OR user JWT)

Case-result endpoints  → BGSTM#303
Artifact endpoints     → BGSTM#298
Audit-log integration  → BGSTM#297
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    get_current_runner_token,  # noqa: F401 — used inside _get_session_auth
    require_runner_scope,
)
from app.crud.audit_log import write_audit
from app.crud.external_results import create_session, finish_session_db, get_session
from app.db.session import get_db
from app.models.runner_token import RunnerToken
from app.schemas.external_results import SessionCreate, SessionFinish, SessionResponse

router = APIRouter()

_WRITE_SCOPE = "external_results:write"
_READ_SCOPE = "external_results:read"


def _session_to_response(session) -> SessionResponse:
    """Map an ExternalRunSession ORM row to a SessionResponse.

    The ci_url column stores a plain string; SessionResponse expects an
    HttpUrl-compatible value.  We pass it through as-is — Pydantic will
    validate and coerce it when constructing the model.
    """
    return SessionResponse(
        id=session.id,
        status=session.status,
        started_at=session.started_at,
        finished_at=session.finished_at,
        runner=session.runner,
        project_id=session.project_id,
        git_sha=session.git_sha,
        git_branch=session.git_branch,
        ci_url=session.ci_url,
        metadata=session.run_metadata or {},
    )


# ---------------------------------------------------------------------------
# POST /external-results/session — start a run
# ---------------------------------------------------------------------------


@router.post(
    "/external-results/session",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_external_session(
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db),
    token: RunnerToken = Depends(require_runner_scope(_WRITE_SCOPE)),
) -> SessionResponse:
    """Start a new external test-run session.

    Returns the existing session if an identical session was created within the
    last 60 seconds (idempotency window).
    """
    session = await create_session(db, payload=payload, runner_token_id=token.id)
    await write_audit(
        db,
        actor_kind="runner_token",
        actor_id=token.id,
        action="external_results.session.start",
        resource_type="external_session",
        resource_id=session.id,
        details={
            "project_id": str(payload.project_id),
            "git_sha": payload.git_sha,
            "git_branch": payload.git_branch,
            "runner": payload.runner,
        },
    )
    return _session_to_response(session)


# ---------------------------------------------------------------------------
# PATCH /external-results/session/{session_id} — finish a run
# ---------------------------------------------------------------------------


@router.patch(
    "/external-results/session/{session_id}",
    response_model=SessionResponse,
)
async def finish_external_session(
    session_id: UUID,
    payload: SessionFinish,
    db: AsyncSession = Depends(get_db),
    token: RunnerToken = Depends(require_runner_scope(_WRITE_SCOPE)),
) -> SessionResponse:
    """Set the terminal status of a session.

    Returns 404 if the session does not exist.
    Returns 409 if the status transition is not allowed (e.g. already finished).
    """
    try:
        session = await finish_session_db(db, session_id=session_id, payload=payload)
    except ValueError as exc:
        detail = exc.args[0]
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "session.not_found", "message": f"Session {session_id} does not exist.", "details": None},
        )

    await write_audit(
        db,
        actor_kind="runner_token",
        actor_id=token.id,
        action="external_results.session.finish",
        resource_type="external_session",
        resource_id=session.id,
        details={
            "status": session.status.value,
            "finished_at": session.finished_at.isoformat() if session.finished_at else None,
        },
    )

    return _session_to_response(session)


# ---------------------------------------------------------------------------
# GET /external-results/session/{session_id} — read a session
# ---------------------------------------------------------------------------


async def _get_session_auth(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """Accept either a runner token or a user JWT for read access.

    We attempt runner-token resolution first; on failure we fall back to user
    JWT.  A 401 is raised only when both paths fail.
    """
    # Try runner-token path
    if authorization and authorization.lower().startswith("bearer bgstm_runner_"):
        from app.auth.dependencies import get_current_runner_token as _get_runner

        try:
            return await _get_runner(authorization=authorization, db=db)
        except HTTPException:
            pass

    # Fall back to user-JWT path via the bearer scheme

    from app.auth.security import decode_access_token
    from app.crud.user import get_user

    if authorization and authorization.lower().startswith("bearer "):
        raw_token = authorization.split(" ", 1)[1]
        payload = decode_access_token(raw_token)
        if payload is not None:
            user_id = payload.get("sub")
            if user_id:
                user = await get_user(db, user_id)
                if user and user.is_active:
                    return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "runner_token.invalid", "message": "Missing or invalid credentials.", "details": None},
    )


@router.get(
    "/external-results/session/{session_id}",
    response_model=SessionResponse,
)
async def get_external_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(_get_session_auth),
) -> SessionResponse:
    """Return a single session by ID.

    Accepts either a runner token (any scope) or a standard user JWT.
    Returns 404 if the session does not exist.
    """
    session = await get_session(db, session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "session.not_found", "message": f"Session {session_id} does not exist.", "details": None},
        )

    return _session_to_response(session)
