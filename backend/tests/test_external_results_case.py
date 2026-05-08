"""Integration tests for External Results case-result endpoints (BGSTM#303)."""

from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.crud.runner_token import create_runner_token
from app.db.session import get_db
from app.main import app
from app.models.audit_log import AuditLog
from app.models.base import Base
from app.models.external_case_result import CaseStatus, ExternalCaseResult
from app.models.link import RequirementTestCaseLink
from app.models.project import Project
from app.models.requirement import PriorityLevel, Requirement, RequirementStatus, RequirementType
from app.models.test_case import TestCase, TestCaseStatus, TestCaseType
from app.models.user import User, UserRole

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


def _session_payload() -> dict[str, str | dict[str, str]]:
    return {
        "runner": "pytest-bgstm@1.0.0",
        "project_id": _PROJECT_ID,
        "git_sha": "abc123",
        "git_branch": "main",
        "ci_url": f"https://ci.example.com/runs/{uuid.uuid4()}",
        "metadata": {"os": "ubuntu-22.04"},
    }


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


@pytest_asyncio.fixture
async def read_token(db_session, admin_user):
    return await create_runner_token(
        db_session,
        label="read-token",
        scopes=["external_results:read"],
        created_by_user_id=admin_user.id,
    )


def _create_session(client: TestClient, plaintext: str) -> str:
    response = client.post("/api/v1/external-results/session", json=_session_payload(), headers=_auth_header(plaintext))
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _create_test_case(db_session: AsyncSession, *, external_id: str | None = None) -> TestCase:
    test_case = TestCase(
        id=uuid.uuid4(),
        external_id=external_id,
        title=f"Case {uuid.uuid4().hex[:6]}",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.DRAFT,
    )
    db_session.add(test_case)
    await db_session.commit()
    await db_session.refresh(test_case)
    return test_case


async def _create_requirement(db_session: AsyncSession) -> Requirement:
    requirement = Requirement(
        id=uuid.uuid4(),
        title=f"Req {uuid.uuid4().hex[:6]}",
        description="desc",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=RequirementStatus.DRAFT,
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)
    return requirement


class TestAutoUpsert:
    @pytest.mark.asyncio
    async def test_test_case_id_exists_links_and_auto_registered_false(self, db_session, write_token):
        _token_model, plaintext = write_token
        existing_test_case = await _create_test_case(db_session)

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            response = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "test_case_id": str(existing_test_case.id),
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [],
                },
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data["test_case_id"] == str(existing_test_case.id)
        assert data["auto_registered"] is False

    @pytest.mark.asyncio
    async def test_test_case_id_missing_returns_404(self, db_session, write_token):
        _token_model, plaintext = write_token

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            response = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "test_case_id": str(uuid.uuid4()),
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [],
                },
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "case.test_case_not_found"

    @pytest.mark.asyncio
    async def test_external_id_existing_links_and_auto_registered_false(self, db_session, write_token):
        _token_model, plaintext = write_token
        existing_test_case = await _create_test_case(db_session, external_id=f"ext-{uuid.uuid4()}")

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            response = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": existing_test_case.external_id,
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [],
                },
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data["test_case_id"] == str(existing_test_case.id)
        assert data["auto_registered"] is False

    @pytest.mark.asyncio
    async def test_external_id_missing_autocreates_test_case(self, db_session, write_token):
        _token_model, plaintext = write_token
        external_id = f"new-ext-{uuid.uuid4()}"

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            response = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": external_id,
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [],
                },
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data["auto_registered"] is True

        created = await db_session.execute(select(TestCase).where(TestCase.id == uuid.UUID(data["test_case_id"])))
        test_case = created.scalar_one_or_none()
        assert test_case is not None
        assert test_case.external_id == external_id
        assert test_case.auto_registered is True


class TestTransitions:
    @pytest.mark.asyncio
    async def test_started_to_passed_allowed(self, db_session, write_token):
        _token_model, plaintext = write_token
        linked_case = await _create_test_case(db_session)

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            manual_case = ExternalCaseResult(
                id=uuid.uuid4(),
                session_id=uuid.UUID(session_id),
                test_case_id=linked_case.id,
                external_id=f"started-{uuid.uuid4()}",
                title="started case",
                outcome=CaseStatus.started,
                duration_ms=1,
                auto_registered=False,
            )
            db_session.add(manual_case)
            await db_session.commit()
            response = client.patch(
                f"/api/v1/external-results/case/{manual_case.id}",
                json={"outcome": "passed"},
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 200, response.text
        assert response.json()["outcome"] == "passed"

    @pytest.mark.asyncio
    async def test_passed_to_flaky_allowed(self, db_session, write_token):
        _token_model, plaintext = write_token
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            create_resp = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"p2f-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [],
                },
                headers=_auth_header(plaintext),
            )
            case_id = create_resp.json()["id"]
            response = client.patch(
                f"/api/v1/external-results/case/{case_id}",
                json={"outcome": "flaky"},
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 200, response.text
        assert response.json()["outcome"] == "flaky"

    @pytest.mark.asyncio
    async def test_passed_to_failed_blocked(self, db_session, write_token):
        _token_model, plaintext = write_token
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            create_resp = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"p2f-block-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [],
                },
                headers=_auth_header(plaintext),
            )
            case_id = create_resp.json()["id"]
            response = client.patch(
                f"/api/v1/external-results/case/{case_id}",
                json={"outcome": "failed"},
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 409
        assert response.json()["detail"]["code"] == "case.transition.invalid"


class TestTraceabilityAndIdempotency:
    @pytest.mark.asyncio
    async def test_valid_requirement_links_and_echoes(self, db_session, write_token):
        _token_model, plaintext = write_token
        requirement = await _create_requirement(db_session)
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            response = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"req-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [str(requirement.id)],
                },
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 201, response.text
        assert response.json()["requirement_ids"] == [str(requirement.id)]

    @pytest.mark.asyncio
    async def test_unknown_requirement_is_unresolved_and_audited(self, db_session, write_token):
        _token_model, plaintext = write_token
        missing_req_id = uuid.uuid4()
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            response = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"missing-req-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [str(missing_req_id)],
                },
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 201, response.text
        assert response.json()["requirement_ids"] == []

        audit_result = await db_session.execute(
            select(AuditLog)
            .where(AuditLog.action == "external_results.case.create")
            .order_by(AuditLog.created_at.desc())
        )
        audit = audit_result.scalar_one()
        assert audit.details["unresolved_requirement_ids"] == [str(missing_req_id)]

    @pytest.mark.asyncio
    async def test_idempotent_external_id_no_duplicate_rows_or_links(self, db_session, write_token):
        _token_model, plaintext = write_token
        requirement = await _create_requirement(db_session)
        external_id = f"idem-{uuid.uuid4()}"
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            payload = {
                "session_id": session_id,
                "external_id": external_id,
                "title": "case",
                "outcome": "passed",
                "duration_ms": 10,
                "requirement_ids": [str(requirement.id)],
            }
            first = client.post("/api/v1/external-results/case", json=payload, headers=_auth_header(plaintext))
            second = client.post("/api/v1/external-results/case", json=payload, headers=_auth_header(plaintext))

        assert first.status_code == 201, first.text
        assert second.status_code == 200, second.text
        assert first.json()["id"] == second.json()["id"]

        link_count_result = await db_session.execute(
            select(func.count())
            .select_from(RequirementTestCaseLink)
            .where(RequirementTestCaseLink.test_case_id == uuid.UUID(first.json()["test_case_id"]))
            .where(RequirementTestCaseLink.requirement_id == requirement.id)
        )
        assert link_count_result.scalar_one() == 1

        idempotent_audit = await db_session.execute(
            select(AuditLog).where(AuditLog.action == "external_results.case.create.idempotent")
        )
        assert idempotent_audit.scalar_one_or_none() is not None


class TestAuditAndAuth:
    @pytest.mark.asyncio
    async def test_create_and_update_write_required_audit_fields(self, db_session, write_token):
        token_model, plaintext = write_token
        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            create_resp = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"audit-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [],
                },
                headers=_auth_header(plaintext),
            )
            case_id = create_resp.json()["id"]
            patch_resp = client.patch(
                f"/api/v1/external-results/case/{case_id}",
                json={"outcome": "flaky"},
                headers=_auth_header(plaintext),
            )

        assert create_resp.status_code == 201, create_resp.text
        assert patch_resp.status_code == 200, patch_resp.text

        create_audits = await db_session.execute(
            select(AuditLog).where(AuditLog.action == "external_results.case.create")
        )
        create_entries = create_audits.scalars().all()
        assert len(create_entries) == 1
        assert create_entries[0].actor_kind == "runner_token"
        assert create_entries[0].actor_token_id == token_model.id
        assert create_entries[0].details["external_id"] is not None

        update_audits = await db_session.execute(
            select(AuditLog).where(AuditLog.action == "external_results.case.update")
        )
        update_entries = update_audits.scalars().all()
        assert len(update_entries) == 1
        assert update_entries[0].details["previous_outcome"] == "passed"
        assert update_entries[0].details["new_outcome"] == "flaky"

    @pytest.mark.asyncio
    async def test_auth_requirements(self, db_session, write_token, read_token):
        _write_model, write_plaintext = write_token
        _read_model, read_plaintext = read_token

        with TestClient(app) as client:
            session_id = _create_session(client, write_plaintext)

            missing_auth_post = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"auth-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [],
                },
            )
            no_write_scope_post = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"auth-scope-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [],
                },
                headers=_auth_header(read_plaintext),
            )
            created = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"auth-get-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [],
                },
                headers=_auth_header(write_plaintext),
            )
            case_id = created.json()["id"]

            client.post(
                "/api/v1/auth/register",
                json={
                    "email": "case-admin@example.com",
                    "password": "pass",
                    "full_name": "Case Admin",
                    "role": "admin",
                },
            )
            login = client.post(
                "/api/v1/auth/login",
                json={"email": "case-admin@example.com", "password": "pass"},
            )
            admin_jwt = login.json()["access_token"]

            get_with_user = client.get(
                f"/api/v1/external-results/case/{case_id}",
                headers={"Authorization": f"Bearer {admin_jwt}"},
            )
            get_with_runner = client.get(
                f"/api/v1/external-results/case/{case_id}",
                headers=_auth_header(read_plaintext),
            )
            get_unknown = client.get(
                f"/api/v1/external-results/case/{uuid.uuid4()}",
                headers=_auth_header(read_plaintext),
            )

        assert missing_auth_post.status_code == 401
        assert no_write_scope_post.status_code == 403
        assert get_with_user.status_code == 200
        assert get_with_runner.status_code == 200
        assert get_unknown.status_code == 404
