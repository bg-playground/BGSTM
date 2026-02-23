"""Tests for paginated API endpoints"""

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


async def _make_requirements(session: AsyncSession, count: int) -> list[Requirement]:
    reqs = [
        Requirement(
            id=uuid.uuid4(),
            external_id=f"REQ-{i:03d}",
            title=f"Requirement {i}",
            description=f"Description {i}",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.MEDIUM,
            status=RequirementStatus.APPROVED,
        )
        for i in range(count)
    ]
    session.add_all(reqs)
    await session.commit()
    return reqs


async def _make_test_cases(session: AsyncSession, count: int) -> list[TestCase]:
    tcs = [
        TestCase(
            id=uuid.uuid4(),
            external_id=f"TC-{i:03d}",
            title=f"Test Case {i}",
            description=f"Description {i}",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.MEDIUM,
            status=TestCaseStatus.READY,
            automation_status=AutomationStatus.MANUAL,
        )
        for i in range(count)
    ]
    session.add_all(tcs)
    await session.commit()
    return tcs


# ── Requirements pagination tests ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_requirements_paginated_structure(db_session):
    """Test paginated requirements endpoint returns correct structure"""
    await _make_requirements(db_session, 5)
    with TestClient(app) as client:
        response = client.get("/api/v1/requirements?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "pages" in data
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert len(data["items"]) == 5


@pytest.mark.asyncio
async def test_list_requirements_page2(db_session):
    """Test page 2 returns different items than page 1"""
    await _make_requirements(db_session, 5)
    with TestClient(app) as client:
        page1 = client.get("/api/v1/requirements?page=1&page_size=3").json()
        page2 = client.get("/api/v1/requirements?page=2&page_size=3").json()
    assert len(page1["items"]) == 3
    assert len(page2["items"]) == 2
    page1_ids = {r["id"] for r in page1["items"]}
    page2_ids = {r["id"] for r in page2["items"]}
    assert page1_ids.isdisjoint(page2_ids)


@pytest.mark.asyncio
async def test_list_requirements_beyond_last_page(db_session):
    """Test page beyond last page returns empty items"""
    await _make_requirements(db_session, 3)
    with TestClient(app) as client:
        response = client.get("/api/v1/requirements?page=10&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_list_requirements_custom_page_size(db_session):
    """Test custom page_size works"""
    await _make_requirements(db_session, 10)
    with TestClient(app) as client:
        response = client.get("/api/v1/requirements?page=1&page_size=4")
    data = response.json()
    assert len(data["items"]) == 4
    assert data["total"] == 10
    assert data["pages"] == 3


# ── Test Cases pagination tests ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_test_cases_paginated_structure(db_session):
    """Test paginated test cases endpoint returns correct structure"""
    await _make_test_cases(db_session, 4)
    with TestClient(app) as client:
        response = client.get("/api/v1/test-cases?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] == 4
    assert data["pages"] == 1


# ── Links pagination tests ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_links_paginated_structure(db_session):
    """Test paginated links endpoint returns correct structure"""
    reqs = await _make_requirements(db_session, 2)
    tcs = await _make_test_cases(db_session, 2)
    db_session.add_all(
        [
            RequirementTestCaseLink(
                id=uuid.uuid4(),
                requirement_id=reqs[0].id,
                test_case_id=tcs[0].id,
                link_type=LinkType.COVERS,
                link_source=LinkSource.MANUAL,
            ),
            RequirementTestCaseLink(
                id=uuid.uuid4(),
                requirement_id=reqs[1].id,
                test_case_id=tcs[1].id,
                link_type=LinkType.COVERS,
                link_source=LinkSource.MANUAL,
            ),
        ]
    )
    await db_session.commit()
    with TestClient(app) as client:
        response = client.get("/api/v1/links?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] == 2


# ── Suggestions pagination tests ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_pending_suggestions_paginated_structure(db_session):
    """Test paginated pending suggestions endpoint returns correct structure"""
    reqs = await _make_requirements(db_session, 2)
    tcs = await _make_test_cases(db_session, 2)
    db_session.add_all(
        [
            LinkSuggestion(
                id=uuid.uuid4(),
                requirement_id=reqs[0].id,
                test_case_id=tcs[0].id,
                similarity_score=0.8,
                suggestion_method=SuggestionMethod.KEYWORD_MATCH,
                status=SuggestionStatus.PENDING,
            ),
            LinkSuggestion(
                id=uuid.uuid4(),
                requirement_id=reqs[1].id,
                test_case_id=tcs[1].id,
                similarity_score=0.6,
                suggestion_method=SuggestionMethod.KEYWORD_MATCH,
                status=SuggestionStatus.PENDING,
            ),
        ]
    )
    await db_session.commit()
    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions/pending?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 2


@pytest.mark.asyncio
async def test_pending_suggestions_preserves_filters(db_session):
    """Test that existing filter params still work alongside pagination"""
    reqs = await _make_requirements(db_session, 2)
    tcs = await _make_test_cases(db_session, 2)
    db_session.add_all(
        [
            LinkSuggestion(
                id=uuid.uuid4(),
                requirement_id=reqs[0].id,
                test_case_id=tcs[0].id,
                similarity_score=0.9,
                suggestion_method=SuggestionMethod.KEYWORD_MATCH,
                status=SuggestionStatus.PENDING,
            ),
            LinkSuggestion(
                id=uuid.uuid4(),
                requirement_id=reqs[1].id,
                test_case_id=tcs[1].id,
                similarity_score=0.3,
                suggestion_method=SuggestionMethod.KEYWORD_MATCH,
                status=SuggestionStatus.PENDING,
            ),
        ]
    )
    await db_session.commit()
    with TestClient(app) as client:
        # Filter by min_score=0.7 should only return the 0.9 score suggestion
        response = client.get("/api/v1/suggestions/pending?min_score=0.7&page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["similarity_score"] >= 0.7
