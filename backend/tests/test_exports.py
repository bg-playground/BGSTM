"""Tests for export endpoints: PDF traceability matrix, suggestions CSV, metrics CSV"""

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
from app.models.requirement import PriorityLevel, Requirement, RequirementStatus, RequirementType
from app.models.suggestion import LinkSuggestion, SuggestionMethod, SuggestionStatus
from app.models.test_case import AutomationStatus, TestCase, TestCaseStatus, TestCaseType
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


async def _seed_data(session: AsyncSession):
    """Create sample data for export tests."""
    req1 = Requirement(
        id=uuid.uuid4(),
        external_id="REQ-001",
        title="User Authentication",
        description="System must support user login",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED,
    )
    req2 = Requirement(
        id=uuid.uuid4(),
        external_id="REQ-002",
        title="Data Export",
        description="System must allow data export",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=RequirementStatus.APPROVED,
    )
    tc1 = TestCase(
        id=uuid.uuid4(),
        external_id="TC-001",
        title="Test Login Functionality",
        description="Test user login",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.AUTOMATED,
    )
    tc2 = TestCase(
        id=uuid.uuid4(),
        external_id="TC-002",
        title="Test Export CSV",
        description="Test export feature",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )
    session.add_all([req1, req2, tc1, tc2])
    await session.flush()

    link1 = RequirementTestCaseLink(
        id=uuid.uuid4(),
        requirement_id=req1.id,
        test_case_id=tc1.id,
        link_type=LinkType.COVERS,
        link_source=LinkSource.MANUAL,
        created_by="test_user",
    )
    session.add(link1)
    await session.flush()

    sugg1 = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req1.id,
        test_case_id=tc1.id,
        similarity_score=0.95,
        suggestion_method=SuggestionMethod.HYBRID,
        status=SuggestionStatus.ACCEPTED,
        reviewed_by="test_user",
    )
    sugg2 = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req2.id,
        test_case_id=tc2.id,
        similarity_score=0.65,
        suggestion_method=SuggestionMethod.KEYWORD_MATCH,
        status=SuggestionStatus.PENDING,
    )
    session.add_all([sugg1, sugg2])
    await session.commit()


# ── Traceability Matrix PDF Export ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_export_traceability_matrix_pdf_returns_pdf(db_session):
    """Test that PDF export returns valid PDF content."""
    await _seed_data(db_session)
    with TestClient(app) as client:
        response = client.get("/api/v1/traceability-matrix/export?format=pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    # PDF files start with %PDF
    assert response.content[:4] == b"%PDF"


@pytest.mark.asyncio
async def test_export_traceability_matrix_pdf_content_disposition(db_session):
    """Test that PDF export has correct Content-Disposition header."""
    with TestClient(app) as client:
        response = client.get("/api/v1/traceability-matrix/export?format=pdf")
    assert response.status_code == 200
    assert "traceability_matrix.pdf" in response.headers["content-disposition"]


@pytest.mark.asyncio
async def test_export_traceability_matrix_pdf_requires_auth():
    """Test that PDF export returns 403 without token (no override)."""
    with TestClient(app) as client:
        response = client.get("/api/v1/traceability-matrix/export?format=pdf")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_export_traceability_matrix_csv_still_works(db_session):
    """Test that existing CSV export still works after PDF addition."""
    await _seed_data(db_session)
    with TestClient(app) as client:
        response = client.get("/api/v1/traceability-matrix/export?format=csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    content = response.text
    assert "Requirement ID" in content
    assert "Test Case ID" in content


@pytest.mark.asyncio
async def test_export_traceability_matrix_json_still_works(db_session):
    """Test that existing JSON export still works after PDF addition."""
    await _seed_data(db_session)
    with TestClient(app) as client:
        response = client.get("/api/v1/traceability-matrix/export?format=json")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]


# ── Suggestions CSV Export ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_export_suggestions_csv_returns_csv(db_session):
    """Test that suggestions CSV export returns valid CSV."""
    await _seed_data(db_session)
    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_suggestions_csv_has_expected_headers(db_session):
    """Test that suggestions CSV export has expected column headers."""
    await _seed_data(db_session)
    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions/export/csv")
    assert response.status_code == 200
    first_line = response.text.splitlines()[0]
    assert "ID" in first_line
    assert "Requirement Title" in first_line
    assert "Test Case Title" in first_line
    assert "Algorithm" in first_line
    assert "Confidence Score" in first_line
    assert "Status" in first_line


@pytest.mark.asyncio
async def test_export_suggestions_csv_filter_by_status(db_session):
    """Test that suggestions CSV export filters by status correctly."""
    await _seed_data(db_session)
    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions/export/csv?status=accepted")
    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    # Header + 1 accepted suggestion
    assert len(lines) == 2
    assert "accepted" in lines[1].lower()


@pytest.mark.asyncio
async def test_export_suggestions_csv_filter_by_algorithm(db_session):
    """Test that suggestions CSV export filters by algorithm correctly."""
    await _seed_data(db_session)
    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions/export/csv?algorithm=hybrid")
    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    # Header + 1 hybrid suggestion
    assert len(lines) == 2
    assert "hybrid" in lines[1].lower()


@pytest.mark.asyncio
async def test_export_suggestions_csv_filter_by_score(db_session):
    """Test that suggestions CSV export filters by score range."""
    await _seed_data(db_session)
    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions/export/csv?min_score=0.9")
    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    # Header + only the 0.95 score suggestion
    assert len(lines) == 2


@pytest.mark.asyncio
async def test_export_suggestions_csv_invalid_status(db_session):
    """Test that invalid status returns 400."""
    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions/export/csv?status=invalid_status")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_export_suggestions_csv_requires_auth():
    """Test that suggestions CSV export returns 403 without token."""
    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions/export/csv")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_export_suggestions_csv_content_disposition(db_session):
    """Test that suggestions CSV has correct Content-Disposition header."""
    with TestClient(app) as client:
        response = client.get("/api/v1/suggestions/export/csv")
    assert response.status_code == 200
    assert "suggestions.csv" in response.headers["content-disposition"]


# ── Metrics CSV Export ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_export_metrics_csv_returns_csv(db_session):
    """Test that metrics CSV export returns valid CSV."""
    await _seed_data(db_session)
    with TestClient(app) as client:
        response = client.get("/api/v1/metrics/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_metrics_csv_has_expected_content(db_session):
    """Test that metrics CSV export has expected sections."""
    await _seed_data(db_session)
    with TestClient(app) as client:
        response = client.get("/api/v1/metrics/export/csv")
    assert response.status_code == 200
    content = response.text
    assert "Coverage Statistics" in content
    assert "Coverage Percentage" in content
    assert "Suggestion Counts by Status" in content
    assert "Algorithm Breakdown" in content


@pytest.mark.asyncio
async def test_export_metrics_csv_requires_auth():
    """Test that metrics CSV export returns 403 without token."""
    with TestClient(app) as client:
        response = client.get("/api/v1/metrics/export/csv")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_export_metrics_csv_content_disposition(db_session):
    """Test that metrics CSV has correct Content-Disposition header."""
    with TestClient(app) as client:
        response = client.get("/api/v1/metrics/export/csv")
    assert response.status_code == 200
    assert "metrics.csv" in response.headers["content-disposition"]
