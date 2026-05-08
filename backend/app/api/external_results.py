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

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    get_runner_or_user_auth,
    require_runner_scope,
)
from app.crud.audit_log import write_audit
from app.crud.external_case_results import create_case_result, get_case_result, update_case_result
from app.crud.external_results import create_session, finish_session_db, get_session
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


def _case_result_to_response(case_result) -> CaseResultResponse:
    return CaseResultResponse(
        id=case_result.id,
        session_id=case_result.session_id,
        test_case_id=case_result.test_case_id,
        external_id=case_result.external_id,
        title=case_result.title,
        outcome=case_result.outcome,
        duration_ms=case_result.duration_ms,
        error_message=case_result.error_message,
        requirement_ids=getattr(case_result, "requirement_ids", []),
        created_at=case_result.created_at,
        auto_registered=case_result.auto_registered,
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


@router.get(
    "/external-results/session/{session_id}",
    response_model=SessionResponse,
)
async def get_external_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(get_runner_or_user_auth),
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
# POST /external-results/case — create a case result
# ---------------------------------------------------------------------------


@router.post(
    "/external-results/case",
    response_model=CaseResultResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_external_case_result(
    payload: CaseResultCreate,
    response: Response,
    db: AsyncSession = Depends(get_db),
    token: RunnerToken = Depends(require_runner_scope(_WRITE_SCOPE)),
) -> CaseResultResponse:
    try:
        case_result, created = await create_case_result(
            db,
            session_id=payload.session_id,
            payload=payload,
            runner_token_id=token.id,
        )
    except ValueError as exc:
        detail = exc.args[0]
        if isinstance(detail, dict) and detail.get("code") in {"case.session_not_found", "case.test_case_not_found"}:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail) from exc
        raise

    if created:
        await write_audit(
            db,
            actor_kind="runner_token",
            actor_id=token.id,
            action="external_results.case.create",
            resource_type="external_case_result",
            resource_id=case_result.id,
            details={
                "session_id": str(case_result.session_id),
                "outcome": case_result.outcome.value,
                "external_id": case_result.external_id,
                "test_case_id": str(case_result.test_case_id) if case_result.test_case_id is not None else None,
                "auto_registered": case_result.auto_registered,
                "unresolved_requirement_ids": [
                    str(requirement_id) for requirement_id in getattr(case_result, "unresolved_requirement_ids", [])
                ],
            },
        )
    else:
        response.status_code = status.HTTP_200_OK
        await write_audit(
            db,
            actor_kind="runner_token",
            actor_id=token.id,
            action="external_results.case.create.idempotent",
            resource_type="external_case_result",
            resource_id=case_result.id,
            details={
                "matched_case_result_id": str(case_result.id),
                "reason": "external_id_collision",
            },
        )

    return _case_result_to_response(case_result)


# ---------------------------------------------------------------------------
# PATCH /external-results/case/{case_result_id} — update a case result
# ---------------------------------------------------------------------------


@router.patch(
    "/external-results/case/{case_result_id}",
    response_model=CaseResultResponse,
)
async def patch_external_case_result(
    case_result_id: UUID,
    payload: CaseResultUpdate,
    db: AsyncSession = Depends(get_db),
    token: RunnerToken = Depends(require_runner_scope(_WRITE_SCOPE)),
) -> CaseResultResponse:
    previous = await get_case_result(db, case_result_id)
    if previous is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "case.not_found",
                "message": f"Case result {case_result_id} does not exist.",
                "details": None,
            },
        )

    previous_outcome = previous.outcome.value

    try:
        case_result = await update_case_result(db, case_result_id=case_result_id, payload=payload)
    except ValueError as exc:
        detail = exc.args[0]
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc
    if case_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "case.not_found",
                "message": f"Case result {case_result_id} does not exist.",
                "details": None,
            },
        )

    details = {
        "previous_outcome": previous_outcome,
        "new_outcome": case_result.outcome.value,
    }
    if payload.duration_ms is not None:
        details["duration_ms"] = payload.duration_ms
    if payload.error_message is not None:
        details["error_message"] = payload.error_message

    await write_audit(
        db,
        actor_kind="runner_token",
        actor_id=token.id,
        action="external_results.case.update",
        resource_type="external_case_result",
        resource_id=case_result.id,
        details=details,
    )
    return _case_result_to_response(case_result)


# ---------------------------------------------------------------------------
# GET /external-results/case/{case_result_id} — read a case result
# ---------------------------------------------------------------------------


@router.get(
    "/external-results/case/{case_result_id}",
    response_model=CaseResultResponse,
)
async def get_external_case_result(
    case_result_id: UUID,
    db: AsyncSession = Depends(get_db),
    _auth=Depends(get_runner_or_user_auth),
) -> CaseResultResponse:
    case_result = await get_case_result(db, case_result_id)
    if case_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "case.not_found",
                "message": f"Case result {case_result_id} does not exist.",
                "details": None,
            },
        )
    return _case_result_to_response(case_result)
