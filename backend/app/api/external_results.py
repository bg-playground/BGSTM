"""API router for External Results — session, case-result, and artifact endpoints.

Implements:
  POST   /external-results/session          – start a run (201 Created)
  PATCH  /external-results/session/{id}     – finish a run
  GET    /external-results/session/{id}     – read a session (runner OR user JWT)
  POST   /external-results/case             – create a case result (BGSTM#303)
  PATCH  /external-results/case/{id}        – update a case result
  GET    /external-results/case/{id}        – read a case result
  POST   /external-results/artifact         – upload an artifact (BGSTM#298)

Audit-log integration  → BGSTM#297
"""

import os
import re
import tempfile
import uuid as _uuid_module
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import (
    get_runner_or_user_auth,
    require_runner_scope,
)
from app.config import settings
from app.crud.audit_log import write_audit
from app.crud.external_case_artifacts import create_artifact
from app.crud.external_case_results import create_case_result, get_case_result, update_case_result
from app.crud.external_results import create_session, finish_session_db, get_session
from app.db.session import get_db
from app.models.external_case_artifact import ArtifactKind
from app.models.runner_token import RunnerToken
from app.schemas.external_results import (
    ArtifactResponse,
    CaseResultCreate,
    CaseResultResponse,
    CaseResultUpdate,
    SessionCreate,
    SessionFinish,
    SessionResponse,
)
from app.storage import get_storage

router = APIRouter()

_WRITE_SCOPE = "external_results:write"
_READ_SCOPE = "external_results:read"
_DEFAULT_RUNNER = "@bgstm/playwright-core@unknown"

# ---------------------------------------------------------------------------
# Artifact upload constants
# ---------------------------------------------------------------------------

# Read the upload stream in 64 KiB chunks.  Tests may monkeypatch this value
# to a smaller number to exercise the streaming / partial-write path.
_ARTIFACT_CHUNK_SIZE: int = 65_536  # 64 KiB

# Content-type allowlist (global).  ``artifact_kind.other`` bypasses this check.
_ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset(
    {
        # Images (screenshot)
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/webp",
        # Video
        "video/webm",
        "video/mp4",
        "video/mpeg",
        # Trace / zip archives
        "application/zip",
        "application/x-zip-compressed",
        "application/octet-stream",
        # Logs / structured data
        "text/plain",
        "application/json",
    }
)

# Filename allowlist: must start with an alphanumeric character, only safe characters, max 255 chars.
# Requiring an initial alphanumeric char naturally blocks dot-only names like "." and "..".
_SAFE_FILENAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,254}$")


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
    normalized_payload = payload.model_copy(
        update={"runner": payload.runner if payload.runner is not None else _DEFAULT_RUNNER}
    )
    session = await create_session(db, payload=normalized_payload, runner_token_id=token.id)
    await write_audit(
        db,
        actor_kind="runner_token",
        actor_id=token.id,
        action="external_results.session.start",
        resource_type="external_session",
        resource_id=session.id,
        details={
            "project_id": str(normalized_payload.project_id),
            "git_sha": normalized_payload.git_sha,
            "git_branch": normalized_payload.git_branch,
            "runner": normalized_payload.runner,
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


# ---------------------------------------------------------------------------
# POST /external-results/artifact — upload an artifact
# ---------------------------------------------------------------------------


def _safe_unlink(path: str) -> None:
    """Remove *path*, silently ignoring missing-file errors."""
    try:
        os.unlink(path)
    except OSError:
        pass


@router.post(
    "/external-results/artifact",
    response_model=ArtifactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_artifact(
    case_result_id: str = Form(...),
    kind: str = Form(...),
    filename: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    token: RunnerToken = Depends(require_runner_scope(_WRITE_SCOPE)),
) -> ArtifactResponse:
    """Upload a binary artifact attached to an existing case result.

    Multipart fields (contract locked at reporter SHA ``ab5d7c1``):
    - ``case_result_id`` — UUID string of the owning case result.
    - ``kind``           — one of ``screenshot``, ``video``, ``trace``, ``log``, ``other``.
    - ``filename``       — original filename including extension.
    - ``file``           — binary body; its ``Content-Type`` part header is used as the
                           artifact content-type.
    """
    # --- Validate kind ---
    try:
        artifact_kind = ArtifactKind(kind)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "validation_error",
                "message": f"Invalid artifact kind: {kind!r}. Must be one of {[k.value for k in ArtifactKind]}.",
                "details": None,
            },
        )

    # --- Sanitize and validate filename (path-traversal defense) ---
    # Reject if the filename differs from its own basename OR fails the allowlist regex.
    # This catches directory components (`../`, `subdir/`, `/etc/`) as well as
    # dangerous characters (null bytes, backslashes, spaces, etc.).
    safe_filename = os.path.basename(filename)
    if safe_filename != filename or not _SAFE_FILENAME_RE.fullmatch(safe_filename):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "validation_error",
                "message": (
                    f"filename {filename!r} is not safe.  filename must contain only "
                    "[A-Za-z0-9._-] characters (1–255) with no path separators."
                ),
                "details": None,
            },
        )

    # --- Validate case_result_id ---
    try:
        case_result_uuid = _uuid_module.UUID(case_result_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "validation_error",
                "message": f"case_result_id {case_result_id!r} is not a valid UUID.",
                "details": None,
            },
        )

    # --- Verify the case result exists ---
    case_result = await get_case_result(db, case_result_uuid)
    if case_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "case_result.not_found",
                "message": f"Case result {case_result_id} does not exist.",
                "details": None,
            },
        )

    # --- Derive content-type from the upload part header ---
    content_type: str = (file.content_type or "application/octet-stream").split(";")[0].strip().lower()

    # --- Validate content-type (bypass for kind=other) ---
    if artifact_kind != ArtifactKind.other and content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "code": "artifact.unsupported_type",
                "message": (
                    f"Content-Type {content_type!r} is not allowed for kind {kind!r}. "
                    f"Allowed types: {sorted(_ALLOWED_CONTENT_TYPES)}."
                ),
                "details": None,
            },
        )

    # --- Stream to a temp file, enforcing max size ---
    max_bytes: int = settings.BGSTM_ARTIFACT_MAX_BYTES
    fd, tmp_path = tempfile.mkstemp(prefix="bgstm_artifact_")
    total_bytes = 0
    try:
        with os.fdopen(fd, "wb") as fp:
            while True:
                chunk = await file.read(_ARTIFACT_CHUNK_SIZE)
                if not chunk:
                    break
                fp.write(chunk)
                total_bytes += len(chunk)
                if total_bytes > max_bytes:
                    # Partial data written — clean up and reject
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail={
                            "code": "artifact.too_large",
                            "message": (f"Artifact exceeds the maximum allowed size of {max_bytes} bytes."),
                            "details": None,
                        },
                    )
    except HTTPException:
        _safe_unlink(tmp_path)
        raise
    except Exception:
        _safe_unlink(tmp_path)
        raise

    # --- Persist via storage backend ---
    storage = get_storage()
    storage_key = f"{case_result_id}/{_uuid_module.uuid4().hex}/{safe_filename}"

    try:
        with open(tmp_path, "rb") as fp:
            result = storage.save(fp, key=storage_key, content_type=content_type)
    finally:
        _safe_unlink(tmp_path)

    # --- Create DB record ---
    artifact = await create_artifact(
        db,
        case_result_id=case_result_uuid,
        kind=artifact_kind,
        filename=safe_filename,
        content_type=content_type,
        size_bytes=result.size_bytes,
        storage_key=result.key,
        url=result.url,
    )

    # --- Audit log (all five fields required by smoke/assert.py) ---
    await write_audit(
        db,
        actor_kind="runner_token",
        actor_id=token.id,
        action="external_results.artifact.upload",
        resource_type="external_case_artifact",
        resource_id=artifact.id,
        details={
            "case_result_id": str(case_result_uuid),
            "kind": artifact_kind.value,
            "size_bytes": result.size_bytes,
            "filename": safe_filename,
            "content_type": content_type,
        },
    )

    await db.commit()
    await db.refresh(artifact)

    return ArtifactResponse(
        id=artifact.id,
        case_result_id=artifact.case_result_id,
        kind=artifact.kind,
        filename=artifact.filename,
        content_type=artifact.content_type,
        size_bytes=artifact.size_bytes,
        url=artifact.url,
        created_at=artifact.created_at,
    )
