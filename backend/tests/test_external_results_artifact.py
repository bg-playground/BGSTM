"""Tests for the artifact upload endpoint (BGSTM#298).

Covers:
- Happy path (201, DB record, audit log, file written to local backend)
- Oversized file → 413, partial write detected, temp file cleaned up
- Bad content-type → 415
- Unknown kind → 422
- Missing case_result_id (FK violation, case not found) → 404
- Bad UUID for case_result_id → 422
- S3 stub raises NotImplementedError
"""

from __future__ import annotations

import io
import os
import tempfile
import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.api.external_results as _api_module
from app.config import settings
from app.crud.runner_token import create_runner_token
from app.db.session import get_db
from app.main import app
from app.models.audit_log import AuditLog
from app.models.base import Base
from app.models.external_case_artifact import ExternalCaseArtifact
from app.models.project import Project
from app.models.user import User, UserRole
from app.storage.s3 import S3Backend

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PROJECT_ID = str(uuid.uuid4())


def _auth_header(plaintext: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {plaintext}"}


def _make_user(role: UserRole = UserRole.admin) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{role.value}-{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashed",
        full_name=f"{role.value.capitalize()} User",
        role=role,
        is_active=True,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        project = Project(id=uuid.UUID(_PROJECT_ID), name=f"project-{uuid.uuid4().hex[:6]}")
        session.add(project)
        await session.commit()

        async def _override_get_db():
            yield session

        app.dependency_overrides[get_db] = _override_get_db
        yield session
        app.dependency_overrides.clear()

    await engine.dispose()


@pytest_asyncio.fixture
async def admin_user(db_session):
    admin = _make_user(UserRole.admin)
    db_session.add(admin)
    await db_session.commit()
    return admin


@pytest_asyncio.fixture
async def write_token(db_session, admin_user):
    return await create_runner_token(
        db_session,
        label="write-token",
        scopes=["external_results:write"],
        created_by_user_id=admin_user.id,
    )


def _session_payload() -> dict:
    return {
        "runner": "pytest-bgstm@1.0.0",
        "project_id": _PROJECT_ID,
        "git_sha": "abc123",
        "git_branch": "main",
        "ci_url": f"https://ci.example.com/runs/{uuid.uuid4()}",
        "metadata": {},
    }


def _create_session(client: TestClient, plaintext: str) -> str:
    resp = client.post(
        "/api/v1/external-results/session",
        json=_session_payload(),
        headers=_auth_header(plaintext),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_case_result(client: TestClient, plaintext: str, session_id: str) -> str:
    resp = client.post(
        "/api/v1/external-results/case",
        json={
            "session_id": session_id,
            "external_id": f"ext-{uuid.uuid4()}",
            "title": "test case",
            "outcome": "passed",
            "duration_ms": 10,
        },
        headers=_auth_header(plaintext),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


class TestHappyPath:
    @pytest.mark.asyncio
    async def test_upload_screenshot_returns_201(self, db_session, write_token, tmp_path, monkeypatch):
        """201 Created with full response body; DB record + audit log written."""
        _token_model, plaintext = write_token

        # Point local backend at a temp directory
        monkeypatch.setattr(settings, "BGSTM_ARTIFACTS_DIR", str(tmp_path))
        monkeypatch.setattr(settings, "BGSTM_ARTIFACT_URL_PREFIX", "http://testserver/artifacts")
        monkeypatch.setattr(settings, "BGSTM_STORAGE_BACKEND", "local")

        file_data = b"\x89PNG\r\n" + b"A" * 100

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            case_result_id = _create_case_result(client, plaintext, session_id)

            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": case_result_id,
                    "kind": "screenshot",
                    "filename": "failure-state.png",
                },
                files={"file": ("failure-state.png", io.BytesIO(file_data), "image/png")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 201, resp.text
        body = resp.json()

        # Response fields
        assert body["case_result_id"] == case_result_id
        assert body["kind"] == "screenshot"
        assert body["filename"] == "failure-state.png"
        assert body["content_type"] == "image/png"
        assert body["size_bytes"] == len(file_data)
        assert "testserver/artifacts" in body["url"]
        assert uuid.UUID(body["id"])  # valid UUID

        # File on disk
        artifact_row = await db_session.execute(
            select(ExternalCaseArtifact).where(ExternalCaseArtifact.id == uuid.UUID(body["id"]))
        )
        artifact = artifact_row.scalar_one()
        assert artifact.size_bytes == len(file_data)
        stored_file = tmp_path / artifact.storage_key
        assert stored_file.exists()
        assert stored_file.read_bytes() == file_data

        # Audit log — all five required fields
        audit_rows = await db_session.execute(
            select(AuditLog).where(AuditLog.action == "external_results.artifact.upload")
        )
        audit = audit_rows.scalar_one()
        assert audit.details["case_result_id"] == case_result_id
        assert audit.details["kind"] == "screenshot"
        assert audit.details["size_bytes"] == len(file_data)
        assert audit.details["filename"] == "failure-state.png"
        assert audit.details["content_type"] == "image/png"


# ---------------------------------------------------------------------------
# Size enforcement (413 + cleanup + partial-write assertion)
# ---------------------------------------------------------------------------


class TestSizeEnforcement:
    @pytest.mark.asyncio
    async def test_oversized_file_returns_413_and_cleans_up(self, db_session, write_token, tmp_path, monkeypatch):
        """413 on oversized upload; streaming abort is now the actual behavior.

        The handler uses streaming-form-data to parse the multipart body and raises
        _SizeLimitExceeded mid-stream as soon as cumulative bytes exceed
        BGSTM_ARTIFACT_MAX_BYTES — bytes past the limit are never read from the
        connection.

        This test exercises the cleanup / DB-row / artifact-dir guarantees post-abort:
          - The handler's own temp file (bgstm_artifact_*) is cleaned up on 413.
          - No artifact row is written to the DB.
          - No file is left in the artifacts directory.
        """
        _token_model, plaintext = write_token

        monkeypatch.setattr(settings, "BGSTM_ARTIFACTS_DIR", str(tmp_path))
        monkeypatch.setattr(settings, "BGSTM_ARTIFACT_URL_PREFIX", "http://testserver/artifacts")
        monkeypatch.setattr(settings, "BGSTM_STORAGE_BACKEND", "local")
        monkeypatch.setattr(settings, "BGSTM_ARTIFACT_MAX_BYTES", 10)
        # Small chunk size so we process the 20-byte file in multiple iterations
        monkeypatch.setattr(_api_module, "_ARTIFACT_CHUNK_SIZE", 8)

        # Track temp files created to verify cleanup
        created_temps: list[str] = []
        real_mkstemp = tempfile.mkstemp

        def _fake_mkstemp(*args, **kwargs):
            fd, path = real_mkstemp(*args, **kwargs)
            created_temps.append(path)
            return fd, path

        monkeypatch.setattr("tempfile.mkstemp", _fake_mkstemp)

        file_data = b"X" * 20  # 20 bytes > max_bytes=10

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            case_result_id = _create_case_result(client, plaintext, session_id)

            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": case_result_id,
                    "kind": "screenshot",
                    "filename": "big.png",
                },
                files={"file": ("big.png", io.BytesIO(file_data), "image/png")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 413, resp.text
        assert resp.json()["detail"]["code"] == "artifact.too_large"

        # Temp file must be cleaned up after 413
        for path in created_temps:
            assert not os.path.exists(path), f"Temp file {path!r} was not cleaned up after 413"

        # No artifact row in DB
        artifact_rows = await db_session.execute(select(ExternalCaseArtifact))
        assert artifact_rows.scalars().all() == []

        # No file in artifacts dir
        artifact_files = list(tmp_path.rglob("*"))
        assert artifact_files == [], f"Unexpected files in artifacts dir: {artifact_files}"

    @pytest.mark.asyncio
    async def test_oversized_upload_aborts_stream_without_reading_full_body(
        self, db_session, write_token, tmp_path, monkeypatch
    ):
        """Verify that bytes past BGSTM_ARTIFACT_MAX_BYTES are NEVER read from the
        request stream. This is the load-bearing test for #320 — it fails against
        the old buffer-then-reject implementation and passes only when streaming
        abort is correctly wired.
        """
        _token_model, plaintext = write_token
        monkeypatch.setattr(settings, "BGSTM_ARTIFACT_MAX_BYTES", 1024)
        monkeypatch.setattr(settings, "BGSTM_ARTIFACTS_DIR", str(tmp_path))
        monkeypatch.setattr(settings, "BGSTM_ARTIFACT_URL_PREFIX", "http://testserver/artifacts")
        monkeypatch.setattr(settings, "BGSTM_STORAGE_BACKEND", "local")

        with TestClient(app) as sync_client:
            session_id = _create_session(sync_client, plaintext)
            case_result_id = _create_case_result(sync_client, plaintext, session_id)

        # Build a multipart body: small text fields + 100 KiB file (100x the 1024 limit).
        LIMIT = 1024
        FILE_SIZE = 100 * LIMIT  # 100 KiB — well past the limit
        boundary = b"bgstmtestboundary"
        file_data = b"X" * FILE_SIZE

        def _field_part(name: str, value: str) -> bytes:
            return (
                b"--"
                + boundary
                + b"\r\n"
                + b'Content-Disposition: form-data; name="'
                + name.encode()
                + b'"\r\n'
                + b"\r\n"
                + value.encode()
                + b"\r\n"
            )

        full_body = (
            _field_part("case_result_id", case_result_id)
            + _field_part("kind", "screenshot")
            + _field_part("filename", "big.png")
            + b"--"
            + boundary
            + b"\r\n"
            + b'Content-Disposition: form-data; name="file"; filename="big.png"\r\n'
            + b"Content-Type: image/png\r\n"
            + b"\r\n"
            + file_data
            + b"\r\n"
            + b"--"
            + boundary
            + b"--\r\n"
        )
        body_size = len(full_body)

        # Track how many bytes our generator has yielded — each yield corresponds
        # to one receive() call from the ASGI server (via ASGITransport).
        bytes_yielded = 0
        CHUNK_SIZE = 4096

        async def streaming_body():
            nonlocal bytes_yielded
            for i in range(0, len(full_body), CHUNK_SIZE):
                chunk = full_body[i : i + CHUNK_SIZE]
                bytes_yielded += len(chunk)
                yield chunk

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            resp = await client.post(
                "/api/v1/external-results/artifact",
                content=streaming_body(),
                headers={
                    "Authorization": f"Bearer {plaintext}",
                    "Content-Type": f"multipart/form-data; boundary={boundary.decode()}",
                },
            )

        assert resp.status_code == 413, resp.text
        assert resp.json()["detail"]["code"] == "artifact.too_large"

        # The server must have stopped reading well before the full body was sent.
        # Allow generous slack (limit + 256 KiB for framing + chunks), but assert
        # well below total body size (100 KiB file ≫ slack).
        assert bytes_yielded < body_size // 2, (
            f"Server read {bytes_yielded} of {body_size} body bytes — "
            "streaming abort is not actually aborting; bytes past the limit are still being read."
        )


# ---------------------------------------------------------------------------
# Malformed multipart body (422 + code=validation_error)
# ---------------------------------------------------------------------------


class TestMalformedMultipart:
    @pytest.mark.asyncio
    async def test_malformed_multipart_returns_422(self, db_session, write_token, tmp_path, monkeypatch):
        """Posting a body that is not valid multipart must return 422 with
        code=validation_error, never 500.
        """
        _token_model, plaintext = write_token
        monkeypatch.setattr(settings, "BGSTM_ARTIFACTS_DIR", str(tmp_path))
        monkeypatch.setattr(settings, "BGSTM_STORAGE_BACKEND", "local")

        from httpx import ASGITransport, AsyncClient

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
            resp = await client.post(
                "/api/v1/external-results/artifact",
                content=b"this is not multipart data at all \x00\x01\x02",
                headers={
                    "Authorization": f"Bearer {plaintext}",
                    # Valid multipart content-type but body is garbage
                    "Content-Type": "multipart/form-data; boundary=correctboundary",
                },
            )

        assert resp.status_code == 422, resp.text
        assert resp.json()["detail"]["code"] == "validation_error"


class TestContentTypeEnforcement:
    @pytest.mark.asyncio
    async def test_disallowed_content_type_returns_415(self, db_session, write_token, tmp_path, monkeypatch):
        _token_model, plaintext = write_token

        monkeypatch.setattr(settings, "BGSTM_ARTIFACTS_DIR", str(tmp_path))
        monkeypatch.setattr(settings, "BGSTM_STORAGE_BACKEND", "local")

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            case_result_id = _create_case_result(client, plaintext, session_id)

            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": case_result_id,
                    "kind": "screenshot",
                    "filename": "attack.exe",
                },
                files={"file": ("attack.exe", io.BytesIO(b"MZ\x00"), "application/x-msdownload")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 415, resp.text
        assert resp.json()["detail"]["code"] == "artifact.unsupported_type"

    @pytest.mark.asyncio
    async def test_other_kind_bypasses_content_type_check(self, db_session, write_token, tmp_path, monkeypatch):
        """kind=other accepts any content-type."""
        _token_model, plaintext = write_token

        monkeypatch.setattr(settings, "BGSTM_ARTIFACTS_DIR", str(tmp_path))
        monkeypatch.setattr(settings, "BGSTM_ARTIFACT_URL_PREFIX", "http://testserver/artifacts")
        monkeypatch.setattr(settings, "BGSTM_STORAGE_BACKEND", "local")

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            case_result_id = _create_case_result(client, plaintext, session_id)

            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": case_result_id,
                    "kind": "other",
                    "filename": "dump.bin",
                },
                files={"file": ("dump.bin", io.BytesIO(b"\x00\x01\x02"), "application/x-custom-binary")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 201, resp.text
        assert resp.json()["kind"] == "other"


# ---------------------------------------------------------------------------
# Path traversal (filename sanitization)
# ---------------------------------------------------------------------------


class TestFilenameValidation:
    """Verify that malicious filenames are rejected before any file is written."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "bad_filename",
        [
            "../etc/passwd",
            "../../tmp/pwned.png",
            "/etc/shadow",
            "subdir/file.png",
            "file\x00.png",  # null byte
            "file\\path.png",  # backslash (also disallowed by regex)
            "a" * 256,  # too long
            ".",  # current directory
            "..",  # parent directory traversal
            "...",  # dots-only
        ],
    )
    async def test_unsafe_filename_returns_422_and_writes_nothing(
        self, db_session, write_token, tmp_path, monkeypatch, bad_filename
    ):
        _token_model, plaintext = write_token
        monkeypatch.setattr(settings, "BGSTM_ARTIFACTS_DIR", str(tmp_path))
        monkeypatch.setattr(settings, "BGSTM_STORAGE_BACKEND", "local")

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            case_result_id = _create_case_result(client, plaintext, session_id)

            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": case_result_id,
                    "kind": "screenshot",
                    "filename": bad_filename,
                },
                files={"file": ("payload", io.BytesIO(b"\x89PNG"), "image/png")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 422, f"Expected 422 for filename={bad_filename!r}, got {resp.status_code}"
        assert resp.json()["detail"]["code"] == "validation_error"

        # Nothing should be written to the artifacts directory
        written = list(tmp_path.rglob("*"))
        assert written == [], f"Files written for malicious filename {bad_filename!r}: {written}"

    @pytest.mark.asyncio
    async def test_local_backend_rejects_escaped_key_directly(self, tmp_path):
        """LocalFsBackend second-line defense: ValueError if key escapes root."""
        from app.storage.local import LocalFsBackend

        backend = LocalFsBackend(root=tmp_path, url_prefix="http://testserver/artifacts")
        with pytest.raises(ValueError, match="escapes artifact root"):
            backend.save(io.BytesIO(b"data"), key="../outside/file.txt", content_type="text/plain")


# ---------------------------------------------------------------------------
# Validation errors (422)
# ---------------------------------------------------------------------------


class TestValidationErrors:
    @pytest.mark.asyncio
    async def test_unknown_kind_returns_422(self, db_session, write_token, tmp_path, monkeypatch):
        _token_model, plaintext = write_token
        monkeypatch.setattr(settings, "BGSTM_ARTIFACTS_DIR", str(tmp_path))
        monkeypatch.setattr(settings, "BGSTM_STORAGE_BACKEND", "local")

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            case_result_id = _create_case_result(client, plaintext, session_id)

            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": case_result_id,
                    "kind": "totally_unknown",
                    "filename": "file.png",
                },
                files={"file": ("file.png", io.BytesIO(b"PNG"), "image/png")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 422
        assert resp.json()["detail"]["code"] == "validation_error"

    @pytest.mark.asyncio
    async def test_invalid_case_result_id_uuid_returns_422(self, db_session, write_token, tmp_path, monkeypatch):
        _token_model, plaintext = write_token
        monkeypatch.setattr(settings, "BGSTM_ARTIFACTS_DIR", str(tmp_path))
        monkeypatch.setattr(settings, "BGSTM_STORAGE_BACKEND", "local")

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": "not-a-uuid",
                    "kind": "screenshot",
                    "filename": "file.png",
                },
                files={"file": ("file.png", io.BytesIO(b"PNG"), "image/png")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 422
        assert resp.json()["detail"]["code"] == "validation_error"


# ---------------------------------------------------------------------------
# FK violation — case_result_id not found (404)
# ---------------------------------------------------------------------------


class TestFKViolation:
    @pytest.mark.asyncio
    async def test_unknown_case_result_id_returns_404(self, db_session, write_token, tmp_path, monkeypatch):
        _token_model, plaintext = write_token
        monkeypatch.setattr(settings, "BGSTM_ARTIFACTS_DIR", str(tmp_path))
        monkeypatch.setattr(settings, "BGSTM_STORAGE_BACKEND", "local")

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": str(uuid.uuid4()),
                    "kind": "screenshot",
                    "filename": "file.png",
                },
                files={"file": ("file.png", io.BytesIO(b"PNG"), "image/png")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 404
        assert resp.json()["detail"]["code"] == "case_result.not_found"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class TestAuth:
    @pytest.mark.asyncio
    async def test_missing_auth_returns_401(self, db_session, write_token, tmp_path, monkeypatch):
        monkeypatch.setattr(settings, "BGSTM_ARTIFACTS_DIR", str(tmp_path))
        monkeypatch.setattr(settings, "BGSTM_STORAGE_BACKEND", "local")
        _token_model, plaintext = write_token

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            case_result_id = _create_case_result(client, plaintext, session_id)

            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": case_result_id,
                    "kind": "screenshot",
                    "filename": "file.png",
                },
                files={"file": ("file.png", io.BytesIO(b"PNG"), "image/png")},
                # No auth header
            )

        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# S3 stub
# ---------------------------------------------------------------------------


class TestS3Stub:
    def test_s3_backend_raises_not_implemented(self):
        backend = S3Backend()
        with pytest.raises(NotImplementedError, match="S3 backend not yet implemented"):
            backend.save(io.BytesIO(b"data"), key="test/key", content_type="image/png")

    def test_s3_url_for_raises_not_implemented(self):
        backend = S3Backend()
        with pytest.raises(NotImplementedError, match="S3 backend not yet implemented"):
            backend.url_for("test/key")
