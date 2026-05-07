"""API router for External Results endpoints.

Implements:
  POST   /external-results/session          – start a run (201 Created)
  PATCH  /external-results/session/{id}     – finish a run
  GET    /external-results/session/{id}     – read a session (runner OR user JWT)
  POST   /external-results/case             – submit case result
  PATCH  /external-results/case/{id}        – update case result
  GET    /external-results/case/{id}        – read case result

Artifact endpoints     → BGSTM#298
Audit-log integration  → BGSTM#297
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Header, HTTPException, Response, status
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    get_current_runner_token,  # noqa: F401 — used inside _get_session_auth
    require_runner_scope,
)
from app.crud.external_results import (
    create_case_result,
    create_session,
    finish_session_db,
    get_case_result,
    get_requirement_ids_for_test_case,
    get_session,
    update_case_result,
)
from app.db.session import get_db
from app.models.runner_token import RunnerToken
from app.schemas.external_results import (
    CaseResultCreate,
    CaseResultResponse,
    CaseResultUpdate,
    SessionCreate,
    SessionFinish,
    SessionResponse,
)

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


async def _case_to_response(db: AsyncSession, case_result, *, auto_registered: bool = False) -> CaseResultResponse:
    requirement_ids = await get_requirement_ids_for_test_case(db, test_case_id=case_result.test_case_id)
    return CaseResultResponse(
        id=case_result.id,
        session_id=case_result.session_id,
        test_case_id=case_result.test_case_id,
        external_id=case_result.external_id,
        title=case_result.title,
        outcome=case_result.outcome,
        duration_ms=case_result.duration_ms,
        error_message=case_result.error_message,
        requirement_ids=requirement_ids,
        created_at=case_result.created_at,
        auto_registered=auto_registered,
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
    token: RunnerToken = Depends(require_runner_scope(_WRITE_SCOPE)),  # noqa: ARG001
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


# ---------------------------------------------------------------------------
# POST /external-results/case — submit a case result
# ---------------------------------------------------------------------------


@router.post(
    "/external-results/case",
    response_model=CaseResultResponse,
)
async def create_external_case_result(
    response: Response,
    payload: dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db),
    token: RunnerToken = Depends(require_runner_scope(_WRITE_SCOPE)),  # noqa: ARG001
) -> CaseResultResponse:
    try:
        case_payload = CaseResultCreate.model_validate(payload)
    except ValidationError as exc:
        missing_identifier = any(
            error.get("msg", "").startswith("Value error, At least one of") for error in exc.errors()
        )
        if missing_identifier:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "missing_identifier",
                    "message": "At least one of 'test_case_id' or 'external_id' must be provided.",
                    "details": None,
                },
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "validation_error",
                "message": "Invalid request payload.",
                "details": {"errors": exc.errors()},
            },
        ) from exc

    try:
        case_result, created, auto_registered = await create_case_result(db, payload=case_payload)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.args[0]) from exc
    except ValueError as exc:
        detail = exc.args[0]
        code = detail.get("code")
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        if code in {"session.not_found", "requirement.not_found"}:
            status_code = status.HTTP_404_NOT_FOUND
        elif code == "session.already_finished":
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(status_code=status_code, detail=detail) from exc

    # TODO(BGSTM#297): write_audit(...) for external_results.case.create/idempotent paths.
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return await _case_to_response(db, case_result, auto_registered=auto_registered)


# ---------------------------------------------------------------------------
# PATCH /external-results/case/{case_result_id} — update case result
# ---------------------------------------------------------------------------


@router.patch(
    "/external-results/case/{case_result_id}",
    response_model=CaseResultResponse,
)
async def patch_external_case_result(
    case_result_id: UUID,
    payload: CaseResultUpdate,
    db: AsyncSession = Depends(get_db),
    token: RunnerToken = Depends(require_runner_scope(_WRITE_SCOPE)),  # noqa: ARG001
) -> CaseResultResponse:
    try:
        case_result = await update_case_result(db, case_result_id=case_result_id, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.args[0]) from exc

    if case_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "case_result.not_found",
                "message": f"Case result {case_result_id} does not exist.",
                "details": None,
            },
        )

    # TODO(BGSTM#297): write_audit(...) for external_results.case.update path.
    return await _case_to_response(db, case_result)


# ---------------------------------------------------------------------------
# GET /external-results/case/{case_result_id} — read case result
# ---------------------------------------------------------------------------


@router.get(
    "/external-results/case/{case_result_id}",
    response_model=CaseResultResponse,
)
async def read_external_case_result(
    case_result_id: UUID,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(_get_session_auth),
) -> CaseResultResponse:
    case_result = await get_case_result(db, case_result_id)
    if case_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "case_result.not_found",
                "message": f"Case result {case_result_id} does not exist.",
                "details": None,
            },
        )
    return await _case_to_response(db, case_result)
