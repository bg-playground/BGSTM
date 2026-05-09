"""Integration tests for External Results case-result endpoints (BGSTM#303)."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.security import create_access_token
from app.crud.runner_token import create_runner_token
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.external_results import ExternalCaseResult
from app.models.link import RequirementTestCaseLink
from app.models.requirement import PriorityLevel, Requirement, RequirementType
from app.models.test_case import TestCase, TestCaseType
from app.models.user import User, UserRole


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
async def read_token(db_session):
    admin = _make_user(UserRole.admin)
    db_session.add(admin)
    await db_session.commit()
    return await create_runner_token(
        db_session,
        label="read-token",
        scopes=["external_results:read"],
        created_by_user_id=admin.id,
    )


@pytest_asyncio.fixture
async def user_jwt(db_session) -> str:
    user = _make_user(UserRole.reviewer)
    db_session.add(user)
    await db_session.commit()
    return create_access_token(data={"sub": str(user.id)})


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _session_payload() -> dict[str, object]:
    return {
        "runner": "pytest-bgstm@1.0.0",
        "project_id": str(uuid.uuid4()),
        "git_sha": "abc123",
        "git_branch": "main",
        "ci_url": f"https://ci.example.com/runs/{uuid.uuid4()}",
        "metadata": {"os": "ubuntu-22.04"},
    }


def _case_payload(session_id: str, **overrides) -> dict:
    payload = {
        "session_id": session_id,
        "title": "suite > login > redirects",
        "outcome": "passed",
        "duration_ms": 1000,
        "error_message": None,
        "external_id": f"suite > login > redirects::{uuid.uuid4()}",
        "test_case_id": None,
        "requirement_ids": [],
    }
    payload.update(overrides)
    return payload


def _create_session(client: TestClient, token: str) -> str:
    resp = client.post("/api/v1/external-results/session", json=_session_payload(), headers=_auth_header(token))
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _create_requirement(db_session: AsyncSession, external_id: str) -> Requirement:
    req = Requirement(
        external_id=external_id,
        title=f"Requirement {external_id}",
        description="desc",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
    )
    db_session.add(req)
    await db_session.commit()
    await db_session.refresh(req)
    return req


class TestCaseAutoUpsert:
    @pytest.mark.asyncio
    async def test_post_with_valid_test_case_id_links_existing_case(self, db_session, write_token):
        _model, plaintext = write_token
        test_case = TestCase(
            external_id=f"TC-{uuid.uuid4().hex[:8]}",
            title="Existing test case",
            description="desc",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.MEDIUM,
        )
        db_session.add(test_case)
        await db_session.commit()
        await db_session.refresh(test_case)

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            resp = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id, test_case_id=str(test_case.id), external_id=None),
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["test_case_id"] == str(test_case.id)
        assert body["auto_registered"] is False

    def test_post_with_missing_test_case_id_returns_404(self, write_token):
        _model, plaintext = write_token
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            resp = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id, test_case_id=str(uuid.uuid4()), external_id=None),
                headers=_auth_header(plaintext),
            )
        assert resp.status_code == 404
        assert resp.json()["detail"]["code"] == "test_case_not_found"

    @pytest.mark.asyncio
    async def test_post_with_existing_external_id_links_without_new_test_case(self, db_session, write_token):
        _model, plaintext = write_token
        external_id = f"ext-{uuid.uuid4().hex}"
        test_case = TestCase(
            external_id=external_id,
            title="Existing by external_id",
            description="desc",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.MEDIUM,
        )
        db_session.add(test_case)
        await db_session.commit()
        await db_session.refresh(test_case)

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            before = await db_session.execute(select(TestCase))
            before_count = len(before.scalars().all())

            resp = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id, external_id=external_id, test_case_id=None),
                headers=_auth_header(plaintext),
            )
            assert resp.status_code == 201, resp.text
            body = resp.json()
            assert body["test_case_id"] == str(test_case.id)
            assert body["auto_registered"] is False

            after = await db_session.execute(select(TestCase))
            after_count = len(after.scalars().all())
            assert before_count == after_count

    @pytest.mark.asyncio
    async def test_post_with_new_external_id_creates_auto_registered_test_case(self, db_session, write_token):
        _model, plaintext = write_token
        external_id = f"new-{uuid.uuid4().hex}"
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            resp = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id, external_id=external_id, test_case_id=None),
                headers=_auth_header(plaintext),
            )

        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["auto_registered"] is True
        assert body["test_case_id"] is not None

        created_test_case = await db_session.get(TestCase, uuid.UUID(body["test_case_id"]))
        assert created_test_case is not None
        assert created_test_case.auto_registered is True
        assert created_test_case.external_id == external_id

    def test_post_without_test_case_id_or_external_id_returns_422(self, write_token):
        _model, plaintext = write_token
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            resp = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id, test_case_id=None, external_id=None),
                headers=_auth_header(plaintext),
            )
        assert resp.status_code == 422
        assert resp.json()["detail"]["code"] == "missing_identifier"


class TestCaseStatusTransitions:
    def test_patch_passed_to_flaky_succeeds(self, write_token):
        _model, plaintext = write_token
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            create_resp = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id, outcome="passed"),
                headers=_auth_header(plaintext),
            )
            assert create_resp.status_code == 201
            case_id = create_resp.json()["id"]

            patch_resp = client.patch(
                f"/api/v1/external-results/case/{case_id}",
                json={"outcome": "flaky"},
                headers=_auth_header(plaintext),
            )

        assert patch_resp.status_code == 200
        assert patch_resp.json()["outcome"] == "flaky"

    def test_patch_passed_to_failed_returns_409(self, write_token):
        _model, plaintext = write_token
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            create_resp = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id, outcome="passed"),
                headers=_auth_header(plaintext),
            )
            assert create_resp.status_code == 201
            case_id = create_resp.json()["id"]

            patch_resp = client.patch(
                f"/api/v1/external-results/case/{case_id}",
                json={"outcome": "failed"},
                headers=_auth_header(plaintext),
            )

        assert patch_resp.status_code == 409
        assert patch_resp.json()["detail"]["code"] == "invalid_status_transition"

    def test_patch_flaky_to_passed_returns_409(self, write_token):
        _model, plaintext = write_token
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            create_resp = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id, outcome="flaky"),
                headers=_auth_header(plaintext),
            )
            assert create_resp.status_code == 201
            case_id = create_resp.json()["id"]

            patch_resp = client.patch(
                f"/api/v1/external-results/case/{case_id}",
                json={"outcome": "passed"},
                headers=_auth_header(plaintext),
            )

        assert patch_resp.status_code == 409
        assert patch_resp.json()["detail"]["code"] == "invalid_status_transition"


class TestCaseTraceabilityAutolink:
    @pytest.mark.asyncio
    async def test_traceability_links_created_and_idempotent(self, db_session, write_token):
        _model, plaintext = write_token
        req1 = await _create_requirement(db_session, external_id=f"REQ-{uuid.uuid4().hex[:8]}")
        req2 = await _create_requirement(db_session, external_id=f"REQ-{uuid.uuid4().hex[:8]}")

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            external_id = f"trace-{uuid.uuid4().hex}"
            payload = _case_payload(
                session_id,
                external_id=external_id,
                requirement_ids=[str(req1.id), str(req2.id)],
            )

            first = client.post("/api/v1/external-results/case", json=payload, headers=_auth_header(plaintext))
            assert first.status_code == 201, first.text
            case_id = first.json()["id"]
            test_case_id = first.json()["test_case_id"]

            second = client.post("/api/v1/external-results/case", json=payload, headers=_auth_header(plaintext))
            assert second.status_code == 200, second.text
            assert second.json()["id"] == case_id
            assert second.json()["test_case_id"] == test_case_id

        links_result = await db_session.execute(
            select(RequirementTestCaseLink).where(RequirementTestCaseLink.test_case_id == uuid.UUID(test_case_id))
        )
        links = links_result.scalars().all()
        assert len(links) == 2


class TestCaseAuth:
    def test_post_patch_with_user_jwt_returns_401(self, user_jwt):
        with TestClient(app) as client:
            session_id = str(uuid.uuid4())
            post_resp = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id),
                headers=_auth_header(user_jwt),
            )
            assert post_resp.status_code == 401

            patch_resp = client.patch(
                f"/api/v1/external-results/case/{uuid.uuid4()}",
                json={"outcome": "flaky"},
                headers=_auth_header(user_jwt),
            )
            assert patch_resp.status_code == 401

    def test_post_patch_with_runner_token_lacking_write_scope_returns_403(self, read_token, write_token):
        _read_model, read_plaintext = read_token
        _write_model, write_plaintext = write_token
        with TestClient(app) as client:
            session_id = _create_session(client, write_plaintext)
            post_resp = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id),
                headers=_auth_header(read_plaintext),
            )
            assert post_resp.status_code == 403

            create_ok = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id),
                headers=_auth_header(write_plaintext),
            )
            assert create_ok.status_code == 201
            case_id = create_ok.json()["id"]

            patch_resp = client.patch(
                f"/api/v1/external-results/case/{case_id}",
                json={"outcome": "flaky"},
                headers=_auth_header(read_plaintext),
            )
            assert patch_resp.status_code == 403

    def test_get_allows_runner_token_or_user_jwt(self, write_token, user_jwt):
        _model, plaintext = write_token
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            create_resp = client.post(
                "/api/v1/external-results/case",
                json=_case_payload(session_id),
                headers=_auth_header(plaintext),
            )
            assert create_resp.status_code == 201
            case_id = create_resp.json()["id"]

            runner_get = client.get(f"/api/v1/external-results/case/{case_id}", headers=_auth_header(plaintext))
            assert runner_get.status_code == 200

            jwt_get = client.get(f"/api/v1/external-results/case/{case_id}", headers=_auth_header(user_jwt))
            assert jwt_get.status_code == 200


class TestCaseIdempotency:
    @pytest.mark.asyncio
    async def test_duplicate_post_same_session_external_id_returns_original(self, db_session, write_token):
        _model, plaintext = write_token
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            external_id = f"idempotent-{uuid.uuid4().hex}"
            payload = _case_payload(session_id, external_id=external_id)

            first = client.post("/api/v1/external-results/case", json=payload, headers=_auth_header(plaintext))
            assert first.status_code == 201, first.text
            case_id = first.json()["id"]

            second = client.post("/api/v1/external-results/case", json=payload, headers=_auth_header(plaintext))
            assert second.status_code == 200, second.text
            assert second.json()["id"] == case_id

        count_result = await db_session.execute(
            select(ExternalCaseResult).where(ExternalCaseResult.session_id == uuid.UUID(session_id))
        )
        assert len(count_result.scalars().all()) == 1


class TestMigrationReversibility:
    def test_downgrade_then_upgrade(self):
        db_url = os.environ.get("DATABASE_URL", "")
        if not db_url.startswith("postgresql"):
            pytest.skip("Migration reversibility test requires PostgreSQL (set DATABASE_URL)")

        backend_dir = str(__import__("pathlib").Path(__file__).parent.parent.parent)
        env = {**os.environ, "DATABASE_URL": db_url}

        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            env=env,
        )
        assert result.returncode == 0, f"upgrade head failed:\n{result.stderr}"

        result = subprocess.run(
            [sys.executable, "-m", "alembic", "downgrade", "-1"],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            env=env,
        )
        assert result.returncode == 0, f"downgrade -1 failed:\n{result.stderr}"

        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=backend_dir,
            env=env,
        )
        assert result.returncode == 0, f"second upgrade head failed:\n{result.stderr}"
