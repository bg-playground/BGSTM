"""Integration tests for the External Results artifact upload endpoint (BGSTM#298).

Covers all 7 acceptance scenarios from the issue:
1. Happy path: upload PNG, get 201, verify DB row, verify file on disk, GET serves bytes
2. Oversize upload returns 413
3. Disallowed content-type returns 415
4. Unknown case_result_id returns 404
5. Invalid kind returns 422
6. Missing/invalid runner token returns 401
7. Cascade: deleting parent external_case_results row also deletes its artifacts
"""

from __future__ import annotations

import uuid
from urllib.parse import urlparse

import pytest
import pytest_asyncio
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.crud.runner_token import create_runner_token
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.external_artifact import ExternalCaseArtifact
from app.models.external_results import ExternalCaseResult
from app.models.user import User, UserRole
from app.storage import get_storage_backend
from app.storage.local import LocalFsBackend

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_SMALL_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


@pytest_asyncio.fixture
async def db_session():
    """In-memory SQLite session with all tables created; overrides get_db."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Enable SQLite foreign-key enforcement so ON DELETE CASCADE is honoured.
    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_con, _connection_record):
        cursor = dbapi_con.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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


@pytest.fixture
def storage_root(tmp_path):
    """Temp directory for artifact storage; overrides the storage backend."""
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    backend = LocalFsBackend(root=artifacts_dir, public_base_url="http://testserver/test-artifacts")
    app.dependency_overrides[get_storage_backend] = lambda: backend

    # Mount a static-files route at /test-artifacts so GET requests work in tests
    try:
        app.mount("/test-artifacts", StaticFiles(directory=str(artifacts_dir)), name="test-artifacts")
        mounted = True
    except Exception:
        mounted = False

    yield artifacts_dir, backend

    app.dependency_overrides.pop(get_storage_backend, None)
    if mounted:
        # Remove the route added above to avoid polluting other tests
        app.routes[:] = [r for r in app.routes if getattr(r, "name", None) != "test-artifacts"]


def _make_user(role: UserRole = UserRole.admin) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{role.value}-{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashed",
        full_name=f"{role.value.capitalize()} User",
        role=role,
        is_active=True,
    )


@pytest_asyncio.fixture
async def write_token(db_session):
    """Runner token with external_results:write scope; returns (model, plaintext)."""
    admin = _make_user(UserRole.admin)
    db_session.add(admin)
    await db_session.commit()
    return await create_runner_token(
        db_session,
        label="write-token",
        scopes=["external_results:write"],
        created_by_user_id=admin.id,
    )


@pytest_asyncio.fixture
async def read_only_token(db_session):
    """Runner token with only external_results:read scope; returns (model, plaintext)."""
    admin = _make_user(UserRole.admin)
    db_session.add(admin)
    await db_session.commit()
    return await create_runner_token(
        db_session,
        label="read-only-token",
        scopes=["external_results:read"],
        created_by_user_id=admin.id,
    )


@pytest_asyncio.fixture
async def case_result(db_session, write_token):
    """A persisted ExternalCaseResult row for use in artifact tests."""
    _model, plaintext = write_token
    headers = {"Authorization": f"Bearer {plaintext}"}

    with TestClient(app) as client:
        # Create a session
        session_resp = client.post(
            "/api/v1/external-results/session",
            json={
                "runner": "pytest@1.0.0",
                "project_id": str(uuid.uuid4()),
                "git_sha": "abc123",
                "git_branch": "main",
            },
            headers=headers,
        )
        assert session_resp.status_code == 201, session_resp.text
        session_id = session_resp.json()["id"]

        # Submit a case result
        case_resp = client.post(
            "/api/v1/external-results/case",
            json={
                "session_id": session_id,
                "title": "login > redirects",
                "outcome": "passed",
                "duration_ms": 500,
                "external_id": f"login::redirects::{uuid.uuid4()}",
            },
            headers=headers,
        )
        assert case_resp.status_code in (200, 201), case_resp.text
        case_result_id = case_resp.json()["id"]

    result = await db_session.execute(
        select(ExternalCaseResult).where(ExternalCaseResult.id == uuid.UUID(case_result_id))
    )
    return result.scalar_one()


def _auth_header(plaintext: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {plaintext}"}


# ---------------------------------------------------------------------------
# 1. Happy path
# ---------------------------------------------------------------------------


class TestArtifactHappyPath:
    def test_upload_png_returns_201_with_artifact_row(self, db_session, write_token, case_result, storage_root):
        artifacts_dir, backend = storage_root
        _model, plaintext = write_token

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": str(case_result.id),
                    "kind": "screenshot",
                    "filename": "screenshot.png",
                },
                files={"file": ("screenshot.png", _SMALL_PNG, "image/png")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["case_result_id"] == str(case_result.id)
        assert body["kind"] == "screenshot"
        assert body["filename"] == "screenshot.png"
        assert body["content_type"] == "image/png"
        assert body["size_bytes"] == len(_SMALL_PNG)
        assert "url" in body
        assert "id" in body
        assert "uploaded_at" in body

    @pytest.mark.asyncio
    async def test_artifact_row_persisted_in_db(self, db_session, write_token, case_result, storage_root):
        _artifacts_dir, _backend = storage_root
        _model, plaintext = write_token

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": str(case_result.id),
                    "kind": "log",
                },
                files={"file": ("output.txt", b"hello world", "text/plain")},
                headers=_auth_header(plaintext),
            )
        assert resp.status_code == 201
        artifact_id = uuid.UUID(resp.json()["id"])

        result = await db_session.execute(select(ExternalCaseArtifact).where(ExternalCaseArtifact.id == artifact_id))
        artifact = result.scalar_one_or_none()
        assert artifact is not None
        assert artifact.content_type == "text/plain"
        assert artifact.size_bytes == len(b"hello world")

    def test_file_written_to_storage_root(self, db_session, write_token, case_result, storage_root):
        artifacts_dir, _backend = storage_root
        _model, plaintext = write_token

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": str(case_result.id),
                    "kind": "screenshot",
                },
                files={"file": ("snap.png", _SMALL_PNG, "image/png")},
                headers=_auth_header(plaintext),
            )
        assert resp.status_code == 201
        storage_key = resp.json().get("url", "").split("/test-artifacts/", 1)[-1]
        stored_file = artifacts_dir / storage_key
        assert stored_file.exists()
        assert stored_file.read_bytes() == _SMALL_PNG

    def test_get_on_returned_url_serves_bytes(self, db_session, write_token, case_result, storage_root):
        _artifacts_dir, _backend = storage_root
        _model, plaintext = write_token

        with TestClient(app) as client:
            upload_resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": str(case_result.id),
                    "kind": "screenshot",
                },
                files={"file": ("shot.png", _SMALL_PNG, "image/png")},
                headers=_auth_header(plaintext),
            )
            assert upload_resp.status_code == 201

            url = upload_resp.json()["url"]
            # Strip the scheme+host to get the path for TestClient
            path = urlparse(url).path
            get_resp = client.get(path)

        assert get_resp.status_code == 200
        assert get_resp.content == _SMALL_PNG


# ---------------------------------------------------------------------------
# 2. Oversize upload returns 413
# ---------------------------------------------------------------------------


class TestArtifactTooLarge:
    def test_oversize_upload_returns_413(self, db_session, write_token, case_result, storage_root):
        from app.config import settings

        _model, plaintext = write_token
        # Create a payload just over the configured limit
        over_limit = settings.STORAGE_MAX_UPLOAD_BYTES + 1
        big_body = b"x" * over_limit

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={"case_result_id": str(case_result.id), "kind": "other"},
                files={"file": ("big.txt", big_body, "text/plain")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 413
        assert resp.json()["detail"]["code"] == "artifact.too_large"

    def test_oversize_upload_with_lower_limit(self, db_session, write_token, case_result, storage_root, monkeypatch):
        """Lowering the limit to 10 bytes causes a 1 KB upload to fail with 413."""
        from app.config import settings as _settings

        monkeypatch.setattr(_settings, "STORAGE_MAX_UPLOAD_BYTES", 10)

        _model, plaintext = write_token

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={"case_result_id": str(case_result.id), "kind": "log"},
                files={"file": ("log.txt", b"a" * 1024, "text/plain")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 413


# ---------------------------------------------------------------------------
# 3. Disallowed content type returns 415
# ---------------------------------------------------------------------------


class TestArtifactDisallowedContentType:
    def test_disallowed_content_type_returns_415(self, db_session, write_token, case_result, storage_root):
        _model, plaintext = write_token

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={"case_result_id": str(case_result.id), "kind": "other"},
                files={"file": ("script.sh", b"#!/bin/bash\necho hi", "application/x-sh")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 415
        assert resp.json()["detail"]["code"] == "artifact.unsupported_content_type"


# ---------------------------------------------------------------------------
# 4. Unknown case_result_id returns 404
# ---------------------------------------------------------------------------


class TestArtifactUnknownCaseResult:
    def test_unknown_case_result_id_returns_404(self, db_session, write_token, storage_root):
        _model, plaintext = write_token

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": str(uuid.uuid4()),
                    "kind": "screenshot",
                },
                files={"file": ("shot.png", _SMALL_PNG, "image/png")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 404
        assert resp.json()["detail"]["code"] == "case_result.not_found"


# ---------------------------------------------------------------------------
# 5. Invalid kind returns 422
# ---------------------------------------------------------------------------


class TestArtifactInvalidKind:
    def test_invalid_kind_returns_422(self, db_session, write_token, case_result, storage_root):
        _model, plaintext = write_token

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={
                    "case_result_id": str(case_result.id),
                    "kind": "not_a_valid_kind",
                },
                files={"file": ("shot.png", _SMALL_PNG, "image/png")},
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# 6. Missing/invalid runner token returns 401
# ---------------------------------------------------------------------------


class TestArtifactAuth:
    def test_missing_token_returns_401_or_422(self, db_session, case_result, storage_root):
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={"case_result_id": str(case_result.id), "kind": "screenshot"},
                files={"file": ("shot.png", _SMALL_PNG, "image/png")},
            )
        assert resp.status_code in (401, 422)

    def test_invalid_token_returns_401(self, db_session, case_result, storage_root):
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={"case_result_id": str(case_result.id), "kind": "screenshot"},
                files={"file": ("shot.png", _SMALL_PNG, "image/png")},
                headers={"Authorization": "Bearer bgstm_runner_invalid_token"},
            )
        assert resp.status_code == 401

    def test_read_only_token_returns_403(self, db_session, case_result, read_only_token, storage_root):
        """A token with only read scope should be rejected with 403."""
        _model, plaintext = read_only_token
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={"case_result_id": str(case_result.id), "kind": "screenshot"},
                files={"file": ("shot.png", _SMALL_PNG, "image/png")},
                headers=_auth_header(plaintext),
            )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 7. Cascade: deleting parent case_result deletes artifacts
# ---------------------------------------------------------------------------


class TestArtifactCascadeDelete:
    @pytest.mark.asyncio
    async def test_delete_case_result_cascades_to_artifacts(self, db_session, write_token, case_result, storage_root):
        _model, plaintext = write_token

        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={"case_result_id": str(case_result.id), "kind": "log"},
                files={"file": ("log.txt", b"test log", "text/plain")},
                headers=_auth_header(plaintext),
            )
        assert resp.status_code == 201
        artifact_id = uuid.UUID(resp.json()["id"])

        # Verify artifact exists
        result = await db_session.execute(select(ExternalCaseArtifact).where(ExternalCaseArtifact.id == artifact_id))
        assert result.scalar_one_or_none() is not None

        # Delete the parent case result
        await db_session.delete(case_result)
        await db_session.commit()

        # Artifact should be gone (CASCADE)
        result2 = await db_session.execute(select(ExternalCaseArtifact).where(ExternalCaseArtifact.id == artifact_id))
        assert result2.scalar_one_or_none() is None
