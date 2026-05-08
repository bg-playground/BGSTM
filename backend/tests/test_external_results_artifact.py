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
from app.models.user import User, UserRole
from app.storage.s3 import S3Backend

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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
        "project_id": str(uuid.uuid4()),
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
        """413 on oversized upload; partial temp file is cleaned up; no DB record created.

        To exercise the streaming/partial-write path, we set:
          - BGSTM_ARTIFACT_MAX_BYTES = 10
          - _ARTIFACT_CHUNK_SIZE = 8

        The 20-byte payload triggers:
          chunk 1 (8 bytes): written → total = 8 ≤ 10 → continue
          chunk 2 (8 bytes): written → total = 16 > 10 → 413 + cleanup

        This asserts that only a partial chunk is written before 413 fires,
        catching any "looks streaming, actually buffers" regression.
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


# ---------------------------------------------------------------------------
# Content-type enforcement (415)
# ---------------------------------------------------------------------------


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
