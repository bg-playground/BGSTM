"""Tests for API endpoints in app/api/links.py"""

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
from app.models.requirement import (
    PriorityLevel,
    Requirement,
    RequirementStatus,
    RequirementType,
)
from app.models.suggestion import LinkSuggestion, SuggestionMethod, SuggestionStatus
from app.models.test_case import (
    AutomationStatus,
    TestCase,
    TestCaseStatus,
    TestCaseType,
)
from app.models.user import User, UserRole

# ── Shared test engine / session factory ──────────────────────────────────────


@pytest_asyncio.fixture
async def db_session():
    """Provide an in-memory SQLite session and override the FastAPI dependency."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:

        async def override_get_db():
            yield session

        mock_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            full_name="Test User",
            role=UserRole.admin,
            is_active=True,
        )

        async def override_get_current_user():
            return mock_user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        yield session
        app.dependency_overrides.clear()

    await engine.dispose()


# ── Sample data helpers ────────────────────────────────────────────────────────


async def _add_req_tc(session: AsyncSession):
    req = Requirement(
        id=uuid.uuid4(),
        external_id="REQ-A01",
        title="API Test Requirement",
        description="Requirement used in API tests",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED,
    )
    tc = TestCase(
        id=uuid.uuid4(),
        external_id="TC-A01",
        title="API Test Case",
        description="Test case used in API tests",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )
    session.add_all([req, tc])
    await session.commit()
    return req, tc


# ── Link endpoint tests ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_link_endpoint(db_session):
    req, tc = await _add_req_tc(db_session)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/links",
            json={
                "requirement_id": str(req.id),
                "test_case_id": str(tc.id),
                "link_type": "covers",
                "link_source": "manual",
                "created_by": "api_tester",
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["requirement_id"] == str(req.id)
    assert data["test_case_id"] == str(tc.id)
    assert data["link_type"] == "covers"
    assert data["link_source"] == "manual"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_links_endpoint(db_session):
    req, tc = await _add_req_tc(db_session)
    link = RequirementTestCaseLink(
        id=uuid.uuid4(),
        requirement_id=req.id,
        test_case_id=tc.id,
        link_type=LinkType.COVERS,
        link_source=LinkSource.MANUAL,
    )
    db_session.add(link)
    await db_session.commit()

    with TestClient(app) as client:
        response = client.get("/api/v1/links")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_link_endpoint(db_session):
    req, tc = await _add_req_tc(db_session)
    link = RequirementTestCaseLink(
        id=uuid.uuid4(),
        requirement_id=req.id,
        test_case_id=tc.id,
        link_type=LinkType.VERIFIES,
        link_source=LinkSource.AI_CONFIRMED,
        confidence_score=0.91,
    )
    db_session.add(link)
    await db_session.commit()

    with TestClient(app) as client:
        response = client.get(f"/api/v1/links/{link.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(link.id)
    assert data["link_type"] == "verifies"


@pytest.mark.asyncio
async def test_get_link_endpoint_not_found(db_session):
    with TestClient(app) as client:
        response = client.get(f"/api/v1/links/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_link_endpoint(db_session):
    req, tc = await _add_req_tc(db_session)
    link = RequirementTestCaseLink(
        id=uuid.uuid4(),
        requirement_id=req.id,
        test_case_id=tc.id,
        link_type=LinkType.COVERS,
        link_source=LinkSource.MANUAL,
    )
    db_session.add(link)
    await db_session.commit()

    with TestClient(app) as client:
        response = client.delete(f"/api/v1/links/{link.id}")
    assert response.status_code == 204

    with TestClient(app) as client:
        response = client.get(f"/api/v1/links/{link.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_link_endpoint_not_found(db_session):
    with TestClient(app) as client:
        response = client.delete(f"/api/v1/links/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_requirement_links_endpoint(db_session):
    req, tc = await _add_req_tc(db_session)
    link = RequirementTestCaseLink(
        id=uuid.uuid4(),
        requirement_id=req.id,
        test_case_id=tc.id,
        link_type=LinkType.COVERS,
        link_source=LinkSource.MANUAL,
    )
    db_session.add(link)
    await db_session.commit()

    with TestClient(app) as client:
        response = client.get(f"/api/v1/requirements/{req.id}/links")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["requirement_id"] == str(req.id)


@pytest.mark.asyncio
async def test_get_requirement_links_empty(db_session):
    req_id = uuid.uuid4()
    with TestClient(app) as client:
        response = client.get(f"/api/v1/requirements/{req_id}/links")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_test_case_links_endpoint(db_session):
    req, tc = await _add_req_tc(db_session)
    link = RequirementTestCaseLink(
        id=uuid.uuid4(),
        requirement_id=req.id,
        test_case_id=tc.id,
        link_type=LinkType.COVERS,
        link_source=LinkSource.MANUAL,
    )
    db_session.add(link)
    await db_session.commit()

    with TestClient(app) as client:
        response = client.get(f"/api/v1/test-cases/{tc.id}/links")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["test_case_id"] == str(tc.id)


# ── Suggestion endpoint tests ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_suggestions_endpoint(db_session):
    req, tc = await _add_req_tc(db_session)
    sugg = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req.id,
        test_case_id=tc.id,
        similarity_score=0.82,
        suggestion_method=SuggestionMethod.HYBRID,
        status=SuggestionStatus.PENDING,
    )
    db_session.add(sugg)
    await db_session.commit()

    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_list_pending_suggestions_endpoint(db_session):
    req, tc = await _add_req_tc(db_session)
    pending = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req.id,
        test_case_id=tc.id,
        similarity_score=0.75,
        suggestion_method=SuggestionMethod.HYBRID,
        status=SuggestionStatus.PENDING,
    )
    accepted = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req.id,
        test_case_id=tc.id,
        similarity_score=0.95,
        suggestion_method=SuggestionMethod.HYBRID,
        status=SuggestionStatus.ACCEPTED,
    )
    db_session.add_all([pending, accepted])
    await db_session.commit()

    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions/pending")
    assert response.status_code == 200
    data = response.json()
    assert all(s["status"] == "pending" for s in data)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_list_pending_suggestions_with_filters(db_session):
    req, tc = await _add_req_tc(db_session)
    for score, method in [(0.9, SuggestionMethod.HYBRID), (0.5, SuggestionMethod.KEYWORD_MATCH)]:
        sugg = LinkSuggestion(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=score,
            suggestion_method=method,
            status=SuggestionStatus.PENDING,
        )
        db_session.add(sugg)
    await db_session.commit()

    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions/pending?min_score=0.7&algorithm=hybrid")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["similarity_score"] >= 0.7
    assert data[0]["suggestion_method"] == "hybrid"


@pytest.mark.asyncio
async def test_get_suggestion_endpoint(db_session):
    req, tc = await _add_req_tc(db_session)
    sugg = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req.id,
        test_case_id=tc.id,
        similarity_score=0.77,
        suggestion_method=SuggestionMethod.SEMANTIC_SIMILARITY,
        status=SuggestionStatus.PENDING,
    )
    db_session.add(sugg)
    await db_session.commit()

    with TestClient(app) as client:
        response = client.get(f"/api/v1/suggestions/{sugg.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sugg.id)
    assert data["similarity_score"] == pytest.approx(0.77)


@pytest.mark.asyncio
async def test_get_suggestion_endpoint_not_found(db_session):
    with TestClient(app) as client:
        response = client.get(f"/api/v1/suggestions/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_review_suggestion_endpoint(db_session):
    req, tc = await _add_req_tc(db_session)
    sugg = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req.id,
        test_case_id=tc.id,
        similarity_score=0.88,
        suggestion_method=SuggestionMethod.HYBRID,
        status=SuggestionStatus.PENDING,
    )
    db_session.add(sugg)
    await db_session.commit()

    with TestClient(app) as client:
        response = client.post(
            f"/api/v1/suggestions/{sugg.id}/review",
            json={"status": "accepted", "feedback": "Good match", "reviewed_by": "tester"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["feedback"] == "Good match"
    assert data["reviewed_by"] == "tester"


@pytest.mark.asyncio
async def test_review_suggestion_endpoint_not_found(db_session):
    with TestClient(app) as client:
        response = client.post(
            f"/api/v1/suggestions/{uuid.uuid4()}/review",
            json={"status": "rejected"},
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_bulk_review_suggestions_endpoint(db_session):
    req, tc = await _add_req_tc(db_session)
    sugg_ids = []
    for score in [0.8, 0.7]:
        sugg = LinkSuggestion(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=score,
            suggestion_method=SuggestionMethod.HYBRID,
            status=SuggestionStatus.PENDING,
        )
        db_session.add(sugg)
        sugg_ids.append(str(sugg.id))
    await db_session.commit()

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/suggestions/bulk-review",
            json={
                "suggestion_ids": sugg_ids,
                "status": "accepted",
                "feedback": "Bulk approved",
                "reviewed_by": "admin",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["status"] == "accepted"


@pytest.mark.asyncio
async def test_bulk_review_empty_ids_rejected(db_session):
    """Bulk review with empty list should fail validation."""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/suggestions/bulk-review",
            json={"suggestion_ids": [], "status": "accepted"},
        )
    assert response.status_code == 422
