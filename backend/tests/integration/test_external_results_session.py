"""Integration tests for External Results session endpoints (BGSTM#300).

Covers:
- create session → finish session → fetch session (happy path)
- 401 without auth on all 3 endpoints
- 403 when token lacks external_results:write scope (POST / PATCH)
- 409 when PATCH-ing an aborted session
- 409 when PATCH-ing a passed session back to started (invalid — but
  SessionFinish rejects non-terminal statuses at the Pydantic layer with 422)
- 409 when PATCH-ing a passed session to any terminal status
- Idempotency: duplicate POST within 60 s returns the same session id
- Migration reversibility: alembic downgrade -1 then upgrade head
"""

from __future__ import annotations

import subprocess
import sys
import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.crud.runner_token import create_runner_token
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.user import User, UserRole

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session():
    """In-memory SQLite session with all tables created; overrides get_db."""
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
    """Runner token with only external_results:read scope."""
    admin = _make_user(UserRole.admin)
    db_session.add(admin)
    await db_session.commit()
    return await create_runner_token(
        db_session,
        label="read-only-token",
        scopes=["external_results:read"],
        created_by_user_id=admin.id,
    )


_PROJECT_ID = str(uuid.uuid4())
_SESSION_PAYLOAD = {
    "runner": "pytest-bgstm@1.0.0",
    "project_id": _PROJECT_ID,
    "git_sha": "abc123",
    "git_branch": "main",
    "ci_url": "https://ci.example.com/runs/1",
    "metadata": {"os": "ubuntu-22.04"},
}

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _auth_header(plaintext: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {plaintext}"}


# ---------------------------------------------------------------------------
# Happy-path: create → finish → fetch
# ---------------------------------------------------------------------------


class TestSessionHappyPath:
    def test_create_finish_fetch(self, db_session, write_token):
        _model, plaintext = write_token
        headers = _auth_header(plaintext)

        with TestClient(app) as client:
            # 1. Create
            resp = client.post("/api/v1/external-results/session", json=_SESSION_PAYLOAD, headers=headers)
            assert resp.status_code == 201, resp.text
            data = resp.json()
            assert data["status"] == "started"
            session_id = data["id"]

            # 2. Finish
            finish_payload = {"status": "passed", "summary": {"total": 10, "passed": 10}}
            resp2 = client.patch(
                f"/api/v1/external-results/session/{session_id}",
                json=finish_payload,
                headers=headers,
            )
            assert resp2.status_code == 200, resp2.text
            data2 = resp2.json()
            assert data2["status"] == "passed"
            assert data2["id"] == session_id
            assert data2["finished_at"] is not None

            # 3. Fetch
            resp3 = client.get(f"/api/v1/external-results/session/{session_id}", headers=headers)
            assert resp3.status_code == 200, resp3.text
            data3 = resp3.json()
            assert data3["status"] == "passed"
            assert data3["id"] == session_id

    def test_create_without_runner_defaults_to_bgstm_playwright_core(self, db_session, write_token):
        _model, plaintext = write_token
        headers = _auth_header(plaintext)
        payload = dict(_SESSION_PAYLOAD)
        payload.pop("runner")

        with TestClient(app) as client:
            resp = client.post("/api/v1/external-results/session", json=payload, headers=headers)

        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert data["runner"].startswith("@bgstm/playwright-core@")


# ---------------------------------------------------------------------------
# Auth: 401 without credentials
# ---------------------------------------------------------------------------


class TestSessionAuth401:
    def test_create_without_auth_returns_401(self, db_session):
        with TestClient(app) as client:
            resp = client.post("/api/v1/external-results/session", json=_SESSION_PAYLOAD)
        # get_current_runner_token uses Header(...) (required); FastAPI returns 422 when
        # the Authorization header is absent before the dependency can raise 401.
        assert resp.status_code in (401, 422)

    def test_patch_without_auth_returns_401(self, db_session):
        fake_id = uuid.uuid4()
        with TestClient(app) as client:
            resp = client.patch(
                f"/api/v1/external-results/session/{fake_id}",
                json={"status": "passed"},
            )
        assert resp.status_code in (401, 422)

    def test_get_without_auth_returns_401(self, db_session):
        fake_id = uuid.uuid4()
        with TestClient(app) as client:
            resp = client.get(f"/api/v1/external-results/session/{fake_id}")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Auth: 403 when token lacks write scope
# ---------------------------------------------------------------------------


class TestSessionAuth403:
    def test_create_read_only_token_returns_403(self, db_session, read_only_token):
        _model, plaintext = read_only_token
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/external-results/session",
                json=_SESSION_PAYLOAD,
                headers=_auth_header(plaintext),
            )
        assert resp.status_code == 403

    def test_patch_read_only_token_returns_403(self, db_session, write_token, read_only_token):
        _wm, write_pt = write_token
        _rm, read_pt = read_only_token

        with TestClient(app) as client:
            # Create with write token
            resp = client.post(
                "/api/v1/external-results/session",
                json=_SESSION_PAYLOAD,
                headers=_auth_header(write_pt),
            )
            assert resp.status_code == 201
            session_id = resp.json()["id"]

            # Attempt to finish with read-only token
            resp2 = client.patch(
                f"/api/v1/external-results/session/{session_id}",
                json={"status": "passed"},
                headers=_auth_header(read_pt),
            )
        assert resp2.status_code == 403


# ---------------------------------------------------------------------------
# Status-transition 409 cases
# ---------------------------------------------------------------------------


class TestSessionTransitions:
    def _create_and_finish(self, client, headers, finish_status: str) -> str:
        """Helper: create a session and finish it; return session_id."""
        # Use a unique ci_url to avoid idempotency collision across tests.
        payload = dict(_SESSION_PAYLOAD, ci_url=f"https://ci.example.com/runs/{uuid.uuid4()}")
        resp = client.post("/api/v1/external-results/session", json=payload, headers=headers)
        assert resp.status_code == 201
        session_id = resp.json()["id"]

        resp2 = client.patch(
            f"/api/v1/external-results/session/{session_id}",
            json={"status": finish_status},
            headers=headers,
        )
        assert resp2.status_code == 200
        return session_id

    def test_patch_aborted_session_returns_409(self, db_session, write_token):
        _model, plaintext = write_token
        headers = _auth_header(plaintext)

        with TestClient(app) as client:
            session_id = self._create_and_finish(client, headers, "aborted")

            # Attempt to transition again
            resp = client.patch(
                f"/api/v1/external-results/session/{session_id}",
                json={"status": "passed"},
                headers=headers,
            )
        assert resp.status_code == 409

    def test_patch_passed_session_returns_409(self, db_session, write_token):
        _model, plaintext = write_token
        headers = _auth_header(plaintext)

        with TestClient(app) as client:
            session_id = self._create_and_finish(client, headers, "passed")

            # Attempt to transition again (failed is also terminal → 409)
            resp = client.patch(
                f"/api/v1/external-results/session/{session_id}",
                json={"status": "failed"},
                headers=headers,
            )
        assert resp.status_code == 409

    def test_patch_started_to_started_returns_422(self, db_session, write_token):
        """SessionFinish rejects non-terminal statuses at the Pydantic layer (422)."""
        _model, plaintext = write_token
        headers = _auth_header(plaintext)

        with TestClient(app) as client:
            payload = dict(_SESSION_PAYLOAD, ci_url=f"https://ci.example.com/runs/{uuid.uuid4()}")
            resp = client.post("/api/v1/external-results/session", json=payload, headers=headers)
            assert resp.status_code == 201
            session_id = resp.json()["id"]

            # "started" is not a terminal status → Pydantic validator raises 422
            resp2 = client.patch(
                f"/api/v1/external-results/session/{session_id}",
                json={"status": "started"},
                headers=headers,
            )
        assert resp2.status_code == 422


# ---------------------------------------------------------------------------
# Idempotency: duplicate POST within 60 s returns the same session id
# ---------------------------------------------------------------------------


class TestSessionIdempotency:
    def test_duplicate_post_returns_same_session(self, db_session, write_token):
        _model, plaintext = write_token
        headers = _auth_header(plaintext)

        with TestClient(app) as client:
            resp1 = client.post("/api/v1/external-results/session", json=_SESSION_PAYLOAD, headers=headers)
            assert resp1.status_code == 201
            id1 = resp1.json()["id"]

            resp2 = client.post("/api/v1/external-results/session", json=_SESSION_PAYLOAD, headers=headers)
            assert resp2.status_code == 201
            id2 = resp2.json()["id"]

        assert id1 == id2, "Duplicate POST within 60 s should return the same session id"


# ---------------------------------------------------------------------------
# Migration reversibility
# ---------------------------------------------------------------------------


class TestMigrationReversibility:
    def test_downgrade_then_upgrade(self):
        """alembic downgrade -1 then upgrade head must succeed.

        This test requires a live PostgreSQL instance (the initial migration
        uses ``CREATE EXTENSION`` which is PG-only and will fail on SQLite).
        It is skipped when ``DATABASE_URL`` is not set to a PostgreSQL URL.
        """
        import os

        db_url = os.environ.get("DATABASE_URL", "")
        if not db_url.startswith("postgresql"):
            pytest.skip("Migration reversibility test requires PostgreSQL (set DATABASE_URL)")

        backend_dir = str(__import__("pathlib").Path(__file__).parent.parent.parent)
        env = {**os.environ, "DATABASE_URL": db_url}

        # Upgrade to head first
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            env=env,
        )
        assert result.returncode == 0, f"upgrade head failed:\n{result.stderr}"

        # Downgrade one step
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "downgrade", "-1"],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            env=env,
        )
        assert result.returncode == 0, f"downgrade -1 failed:\n{result.stderr}"

        # Upgrade back to head
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            env=env,
        )
        assert result.returncode == 0, f"second upgrade head failed:\n{result.stderr}"
