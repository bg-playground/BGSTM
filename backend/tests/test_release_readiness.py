import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.link import LinkSource, LinkType, RequirementTestCaseLink
from app.models.release_signoff import ReleaseSignoffRole
from app.models.requirement import PriorityLevel, Requirement, RequirementStatus, RequirementType
from app.models.suggestion import LinkSuggestion, SuggestionMethod, SuggestionStatus
from app.models.test_case import AutomationStatus, TestCase, TestCaseStatus, TestCaseType
from app.models.user import User, UserRole


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:

        async def override_get_db():
            yield session

        admin_user = User(
            id=uuid.uuid4(),
            email="admin@example.com",
            hashed_password="hashed",
            full_name="Admin User",
            role=UserRole.admin,
            is_active=True,
        )
        reviewer_user = User(
            id=uuid.uuid4(),
            email="reviewer@example.com",
            hashed_password="hashed",
            full_name="Reviewer User",
            role=UserRole.reviewer,
            is_active=True,
        )
        session.add_all([admin_user, reviewer_user])
        await session.commit()

        app.dependency_overrides[get_db] = override_get_db
        yield session, admin_user, reviewer_user
        app.dependency_overrides.clear()

    await engine.dispose()


async def _seed_threshold_mix(session: AsyncSession):
    requirements = []
    test_cases = []

    for idx in range(10):
        requirements.append(
            Requirement(
                id=uuid.uuid4(),
                external_id=f"REQ-{idx:03d}",
                title=f"Requirement {idx}",
                description="seeded",
                type=RequirementType.FUNCTIONAL,
                priority=PriorityLevel.MEDIUM,
                status=RequirementStatus.APPROVED,
            )
        )
        test_cases.append(
            TestCase(
                id=uuid.uuid4(),
                external_id=f"TC-{idx:03d}",
                title=f"Test Case {idx}",
                description="seeded",
                type=TestCaseType.FUNCTIONAL,
                priority=PriorityLevel.MEDIUM,
                status=TestCaseStatus.READY,
                automation_status=AutomationStatus.AUTOMATED,
            )
        )

    session.add_all(requirements + test_cases)
    await session.flush()

    links = []
    for idx in range(10):
        links.append(
            RequirementTestCaseLink(
                id=uuid.uuid4(),
                requirement_id=requirements[min(idx, 6)].id,
                test_case_id=test_cases[idx].id,
                link_type=LinkType.COVERS,
                link_source=LinkSource.MANUAL,
                created_by="seed",
            )
        )
    session.add_all(links)

    suggestions = [
        LinkSuggestion(
            id=uuid.uuid4(),
            requirement_id=requirements[7].id,
            test_case_id=test_cases[0].id,
            similarity_score=0.75,
            suggestion_method=SuggestionMethod.HYBRID,
            status=SuggestionStatus.PENDING,
        ),
        LinkSuggestion(
            id=uuid.uuid4(),
            requirement_id=requirements[8].id,
            test_case_id=test_cases[1].id,
            similarity_score=0.72,
            suggestion_method=SuggestionMethod.KEYWORD_MATCH,
            status=SuggestionStatus.PENDING,
        ),
    ]
    session.add_all(suggestions)
    await session.commit()


@pytest.mark.asyncio
async def test_empty_database_snapshot_returns_no_go_with_na(db_session):
    _session, _admin, _reviewer = db_session

    async def override_user():
        return _reviewer

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/release-readiness/")
        assert response.status_code == 200
        payload = response.json()
        assert payload["overall_status"] == "no_go"
        na_criteria = [criterion for criterion in payload["criteria"] if criterion["status"] == "na"]
        assert len(na_criteria) >= 3
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_snapshot_seeded_data_exercises_threshold_bands(db_session):
    session, admin_user, _reviewer = db_session
    await _seed_threshold_mix(session)

    async def override_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/release-readiness/")
        assert response.status_code == 200
        payload = response.json()
        statuses = {criterion["id"]: criterion["status"] for criterion in payload["criteria"]}
        assert statuses["requirements_linked"] == "fail"
        assert statuses["test_cases_linked"] == "pass"
        assert statuses["pending_link_suggestions"] == "warn"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_signoff_lifecycle_create_then_revoke(db_session):
    _session, admin_user, _reviewer = db_session

    async def override_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            create_response = client.post(
                "/api/v1/release-readiness/signoff",
                json={"role": ReleaseSignoffRole.product.value, "note": "Approved"},
            )
            assert create_response.status_code == 200
            snapshot = create_response.json()
            product_signoff = next(item for item in snapshot["signoffs"] if item["role"] == "product")
            assert product_signoff["signed_off"] is True
            assert product_signoff["note"] == "Approved"

            revoke_response = client.delete(f"/api/v1/release-readiness/signoff/{ReleaseSignoffRole.product.value}")
            assert revoke_response.status_code == 200
            revoked_snapshot = revoke_response.json()
            product_after_revoke = next(item for item in revoked_snapshot["signoffs"] if item["role"] == "product")
            assert product_after_revoke["signed_off"] is False
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_signoff_rbac_non_admin_gets_403_for_qa_lead(db_session):
    _session, _admin_user, reviewer_user = db_session

    async def override_user():
        return reviewer_user

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/release-readiness/signoff",
                json={"role": ReleaseSignoffRole.qa_lead.value, "note": "Attempt"},
            )
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_markdown_export_contains_status_criteria_and_roles(db_session):
    _session, admin_user, _reviewer = db_session

    async def override_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/release-readiness/export?format=md")
        assert response.status_code == 200
        assert "text/markdown" in response.headers["content-type"]

        content = response.text
        assert "Overall status" in content
        for label in [
            "Requirements with at least one linked test case",
            "Test cases with at least one linked requirement",
            "Pending link suggestions awaiting review",
            "Test cases with no last_run_status (never executed)",
            "Test cases with last_run_status == 'failed'",
            "All three roles signed off",
        ]:
            assert label in content

        for role in ["qa_lead", "product", "eng_lead"]:
            assert role in content
    finally:
        app.dependency_overrides.pop(get_current_user, None)
