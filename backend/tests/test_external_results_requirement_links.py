"""Requirement-link integration tests for External Results case-result endpoints."""

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
from app.models.link import RequirementTestCaseLink
from app.models.project import Project
from app.models.requirement import PriorityLevel, Requirement, RequirementStatus, RequirementType
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


def _create_session(client: TestClient, plaintext: str) -> str:
    response = client.post("/api/v1/external-results/session", json=_session_payload(), headers=_auth_header(plaintext))
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _create_requirement(
    db_session: AsyncSession,
    *,
    external_id: str | None = None,
) -> Requirement:
    requirement = Requirement(
        id=uuid.uuid4(),
        title=f"Req {uuid.uuid4().hex[:6]}",
        description="desc",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=RequirementStatus.DRAFT,
        external_id=external_id,
    )
    db_session.add(requirement)
    await db_session.commit()
    await db_session.refresh(requirement)
    return requirement


class TestRequirementExternalIds:
    @pytest.mark.asyncio
    async def test_known_external_id_resolves_and_links(self, db_session, write_token):
        _token_model, plaintext = write_token
        requirement = await _create_requirement(db_session, external_id="REQ-KNOWN")

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            response = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"known-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_external_ids": ["REQ-KNOWN"],
                },
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 201, response.text
        assert response.json()["requirement_ids"] == [str(requirement.id)]

        link_count_result = await db_session.execute(
            select(func.count())
            .select_from(RequirementTestCaseLink)
            .where(RequirementTestCaseLink.test_case_id == uuid.UUID(response.json()["test_case_id"]))
            .where(RequirementTestCaseLink.requirement_id == requirement.id)
        )
        assert link_count_result.scalar_one() == 1

    @pytest.mark.asyncio
    async def test_unknown_external_id_without_auto_register_is_audited_and_unlinked(self, db_session, write_token):
        _token_model, plaintext = write_token

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            response = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"missing-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_external_ids": ["REQ-MISSING"],
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
        assert audit.details["requirement_external_ids_submitted"] == ["REQ-MISSING"]
        assert audit.details["unresolved_requirement_external_ids"] == ["REQ-MISSING"]
        assert audit.details["auto_register_requirements"] is False

    @pytest.mark.asyncio
    async def test_unknown_external_id_with_auto_register_creates_requirement_and_link(self, db_session, write_token):
        _token_model, plaintext = write_token

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            response = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"auto-register-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_external_ids": ["REQ-MISSING"],
                    "auto_register_requirements": True,
                },
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 201, response.text
        requirement_id = uuid.UUID(response.json()["requirement_ids"][0])

        requirement_result = await db_session.execute(select(Requirement).where(Requirement.id == requirement_id))
        requirement = requirement_result.scalar_one()
        assert requirement.external_id == "REQ-MISSING"
        assert requirement.title == "REQ-MISSING"
        assert requirement.description == "Auto-registered from external ID REQ-MISSING"
        assert requirement.type == RequirementType.FUNCTIONAL
        assert requirement.priority == PriorityLevel.MEDIUM
        assert requirement.status == RequirementStatus.DRAFT

        link_count_result = await db_session.execute(
            select(func.count())
            .select_from(RequirementTestCaseLink)
            .where(RequirementTestCaseLink.test_case_id == uuid.UUID(response.json()["test_case_id"]))
            .where(RequirementTestCaseLink.requirement_id == requirement.id)
        )
        assert link_count_result.scalar_one() == 1

    @pytest.mark.asyncio
    async def test_mixed_uuid_and_external_ids_deduplicate_union(self, db_session, write_token):
        _token_model, plaintext = write_token
        shared_requirement = await _create_requirement(db_session, external_id="REQ-SHARED")
        uuid_only_requirement = await _create_requirement(db_session)

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            response = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"mixed-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_ids": [str(shared_requirement.id), str(uuid_only_requirement.id)],
                    "requirement_external_ids": ["REQ-SHARED"],
                },
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 201, response.text
        assert set(response.json()["requirement_ids"]) == {
            str(shared_requirement.id),
            str(uuid_only_requirement.id),
        }

        link_count_result = await db_session.execute(
            select(func.count())
            .select_from(RequirementTestCaseLink)
            .where(RequirementTestCaseLink.test_case_id == uuid.UUID(response.json()["test_case_id"]))
        )
        assert link_count_result.scalar_one() == 2

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("submitted_value", "include_field"),
        [
            (None, True),
            ([], True),
            (None, False),
        ],
    )
    async def test_empty_or_null_external_ids_are_noop_and_do_not_pollute_audit(
        self,
        db_session,
        write_token,
        submitted_value,
        include_field,
    ):
        _token_model, plaintext = write_token

        payload: dict[str, object] = {
            "session_id": None,
            "external_id": f"noop-{uuid.uuid4()}",
            "title": "case",
            "outcome": "passed",
            "duration_ms": 10,
        }

        with TestClient(app) as client:
            payload["session_id"] = _create_session(client, plaintext)
            if include_field:
                payload["requirement_external_ids"] = submitted_value
            response = client.post(
                "/api/v1/external-results/case",
                json=payload,
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
        assert "requirement_external_ids_submitted" not in audit.details
        assert "unresolved_requirement_external_ids" not in audit.details
        assert "auto_register_requirements" not in audit.details

    @pytest.mark.asyncio
    async def test_whitespace_only_external_id_entry_returns_422(self, db_session, write_token):
        _token_model, plaintext = write_token

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            response = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"validation-{uuid.uuid4()}",
                    "title": "case",
                    "outcome": "passed",
                    "duration_ms": 10,
                    "requirement_external_ids": ["   "],
                },
                headers=_auth_header(plaintext),
            )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_idempotent_repost_with_same_external_ids_does_not_duplicate_links(self, db_session, write_token):
        _token_model, plaintext = write_token
        requirement = await _create_requirement(db_session, external_id="REQ-IDEMPOTENT")
        external_id = f"idem-{uuid.uuid4()}"
        payload = {
            "external_id": external_id,
            "title": "case",
            "outcome": "passed",
            "duration_ms": 10,
            "requirement_external_ids": ["REQ-IDEMPOTENT"],
        }

        with TestClient(app) as client:
            session_id = _create_session(client, plaintext)
            first = client.post(
                "/api/v1/external-results/case",
                json={"session_id": session_id, **payload},
                headers=_auth_header(plaintext),
            )
            second = client.post(
                "/api/v1/external-results/case",
                json={"session_id": session_id, **payload},
                headers=_auth_header(plaintext),
            )

        assert first.status_code == 201, first.text
        assert second.status_code == 200, second.text
        assert first.json()["id"] == second.json()["id"]
        assert second.json()["requirement_ids"] == [str(requirement.id)]

        link_count_result = await db_session.execute(
            select(func.count())
            .select_from(RequirementTestCaseLink)
            .where(RequirementTestCaseLink.test_case_id == uuid.UUID(first.json()["test_case_id"]))
            .where(RequirementTestCaseLink.requirement_id == requirement.id)
        )
        assert link_count_result.scalar_one() == 1
