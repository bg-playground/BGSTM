"""Tests for Traceability Matrix and Metrics endpoints"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.crud.traceability import get_metrics, get_traceability_matrix
from app.models.base import Base
from app.models.link import LinkSource, LinkType, RequirementTestCaseLink
from app.models.requirement import (
    PriorityLevel,
    Requirement,
    RequirementStatus,
    RequirementType,
)
from app.models.suggestion import (
    LinkSuggestion,
    SuggestionMethod,
    SuggestionStatus,
)
from app.models.test_case import (
    AutomationStatus,
    TestCase,
    TestCaseStatus,
    TestCaseType,
)


async def create_sample_data(session: AsyncSession):
    """Create sample requirements, test cases, links, and suggestions"""
    # Create requirements
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
    req3 = Requirement(
        id=uuid.uuid4(),
        external_id="REQ-003",
        title="Performance",
        description="System must respond within 2 seconds",
        type=RequirementType.NON_FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED,
    )

    # Create test cases
    tc1 = TestCase(
        id=uuid.uuid4(),
        external_id="TC-001",
        title="Test Login Functionality",
        description="Test user login with valid credentials",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.AUTOMATED,
    )
    tc2 = TestCase(
        id=uuid.uuid4(),
        external_id="TC-002",
        title="Test Data Export CSV",
        description="Test exporting data to CSV",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )
    tc3 = TestCase(
        id=uuid.uuid4(),
        external_id="TC-003",
        title="Test Response Time",
        description="Test system response time",
        type=TestCaseType.PERFORMANCE,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.AUTOMATED,
    )
    tc4 = TestCase(
        id=uuid.uuid4(),
        external_id="TC-004",
        title="Orphan Test Case",
        description="This test case has no links",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.LOW,
        status=TestCaseStatus.DRAFT,
        automation_status=AutomationStatus.MANUAL,
    )

    session.add_all([req1, req2, req3, tc1, tc2, tc3, tc4])
    await session.flush()

    # Create links (req1 has manual link, req2 has AI-suggested pending link, req3 has no links)
    link1 = RequirementTestCaseLink(
        id=uuid.uuid4(),
        requirement_id=req1.id,
        test_case_id=tc1.id,
        link_type=LinkType.COVERS,
        link_source=LinkSource.MANUAL,
        created_by="test_user",
    )
    link2 = RequirementTestCaseLink(
        id=uuid.uuid4(),
        requirement_id=req2.id,
        test_case_id=tc2.id,
        link_type=LinkType.COVERS,
        link_source=LinkSource.AI_SUGGESTED,
        confidence_score=0.85,
        created_by="ai_system",
    )
    link3 = RequirementTestCaseLink(
        id=uuid.uuid4(),
        requirement_id=req3.id,
        test_case_id=tc3.id,
        link_type=LinkType.VERIFIES,
        link_source=LinkSource.AI_CONFIRMED,
        confidence_score=0.92,
        created_by="test_user",
    )

    session.add_all([link1, link2, link3])
    await session.flush()

    # Create suggestions
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
        similarity_score=0.75,
        suggestion_method=SuggestionMethod.KEYWORD_MATCH,
        status=SuggestionStatus.PENDING,
    )
    sugg3 = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req2.id,
        test_case_id=tc3.id,
        similarity_score=0.60,
        suggestion_method=SuggestionMethod.SEMANTIC_SIMILARITY,
        status=SuggestionStatus.REJECTED,
        reviewed_by="test_user",
    )
    sugg4 = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req3.id,
        test_case_id=tc3.id,
        similarity_score=0.88,
        suggestion_method=SuggestionMethod.HYBRID,
        status=SuggestionStatus.ACCEPTED,
        reviewed_by="test_user",
    )

    session.add_all([sugg1, sugg2, sugg3, sugg4])
    await session.commit()


@pytest.mark.asyncio
async def test_traceability_matrix_basic():
    """Test basic traceability matrix generation"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        matrix = await get_traceability_matrix(session)

        # Check overall metrics
        assert matrix.total_requirements == 3
        assert matrix.total_test_cases == 4
        assert matrix.covered_requirements == 2  # req1 (manual) and req3 (AI-confirmed)
        assert matrix.uncovered_requirements == 0  # No requirements are truly uncovered (req2 is partially_covered)
        assert matrix.orphan_test_cases == 1  # tc4 has no links

        # Coverage percentage: 2/3 = 66.67%
        assert matrix.coverage_percentage == pytest.approx(66.67, rel=0.1)

        # Check matrix length
        assert len(matrix.matrix) == 3
        assert len(matrix.orphans) == 1

    await engine.dispose()


@pytest.mark.asyncio
async def test_traceability_matrix_coverage_status():
    """Test coverage status classification"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        matrix = await get_traceability_matrix(session)

        # Find each requirement in matrix
        req_coverage = {item.external_id: item for item in matrix.matrix}

        # REQ-001 should be covered (manual link)
        assert req_coverage["REQ-001"].coverage_status == "covered"
        assert len(req_coverage["REQ-001"].linked_test_cases) == 1
        assert req_coverage["REQ-001"].linked_test_cases[0].link_status == "accepted"

        # REQ-002 should be partially covered (only pending link)
        assert req_coverage["REQ-002"].coverage_status == "partially_covered"
        assert len(req_coverage["REQ-002"].linked_test_cases) == 1
        assert req_coverage["REQ-002"].linked_test_cases[0].link_status == "pending"

        # REQ-003 should be covered (AI-confirmed link)
        assert req_coverage["REQ-003"].coverage_status == "covered"
        assert len(req_coverage["REQ-003"].linked_test_cases) == 1
        assert req_coverage["REQ-003"].linked_test_cases[0].link_status == "accepted"

    await engine.dispose()


@pytest.mark.asyncio
async def test_traceability_matrix_orphans():
    """Test orphan test case identification"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        matrix = await get_traceability_matrix(session)

        assert len(matrix.orphans) == 1
        orphan = matrix.orphans[0]
        assert orphan.external_id == "TC-004"
        assert orphan.title == "Orphan Test Case"

    await engine.dispose()


@pytest.mark.asyncio
async def test_traceability_matrix_empty_database():
    """Test traceability matrix with empty database"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        matrix = await get_traceability_matrix(session)

        assert matrix.total_requirements == 0
        assert matrix.total_test_cases == 0
        assert matrix.covered_requirements == 0
        assert matrix.uncovered_requirements == 0
        assert matrix.orphan_test_cases == 0
        assert matrix.coverage_percentage == 0.0
        assert len(matrix.matrix) == 0
        assert len(matrix.orphans) == 0

    await engine.dispose()


@pytest.mark.asyncio
async def test_metrics_basic():
    """Test basic metrics calculation"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        metrics = await get_metrics(session)

        # Check counts
        assert metrics.total_requirements == 3
        assert metrics.total_test_cases == 4
        assert metrics.total_links == 3
        assert metrics.total_suggestions == 4

        # Check suggestion breakdown
        assert metrics.accepted_suggestions == 2
        assert metrics.rejected_suggestions == 1
        assert metrics.pending_suggestions == 1

        # Check link sources
        assert metrics.manual_links == 1
        assert metrics.ai_suggested_links == 2  # AI_CONFIRMED + AI_SUGGESTED

        # Coverage percentage: 2 requirements with accepted links / 3 total = 66.67%
        assert metrics.coverage_percentage == pytest.approx(66.67, rel=0.1)

        # Suggestion acceptance rate: 2 accepted / 4 total = 50%
        assert metrics.suggestion_acceptance_rate == 50.0

    await engine.dispose()


@pytest.mark.asyncio
async def test_metrics_algorithm_breakdown():
    """Test algorithm-specific metrics"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        metrics = await get_metrics(session)

        # Check algorithm breakdown
        assert len(metrics.algorithm_breakdown) == 4  # All enum values

        # Create lookup by algorithm name
        algo_metrics = {algo.algorithm: algo for algo in metrics.algorithm_breakdown}

        # Hybrid: 2 suggestions (2 accepted, 0 rejected, 0 pending) = 100% acceptance
        assert algo_metrics["hybrid"].total_suggestions == 2
        assert algo_metrics["hybrid"].accepted_suggestions == 2
        assert algo_metrics["hybrid"].acceptance_rate == 100.0

        # Keyword: 1 suggestion (0 accepted, 0 rejected, 1 pending) = 0% acceptance
        assert algo_metrics["keyword_match"].total_suggestions == 1
        assert algo_metrics["keyword_match"].pending_suggestions == 1
        assert algo_metrics["keyword_match"].acceptance_rate == 0.0

        # Semantic: 1 suggestion (0 accepted, 1 rejected, 0 pending) = 0% acceptance
        assert algo_metrics["semantic_similarity"].total_suggestions == 1
        assert algo_metrics["semantic_similarity"].rejected_suggestions == 1
        assert algo_metrics["semantic_similarity"].acceptance_rate == 0.0

        # Heuristic: 0 suggestions
        assert algo_metrics["heuristic"].total_suggestions == 0
        assert algo_metrics["heuristic"].acceptance_rate == 0.0

    await engine.dispose()


@pytest.mark.asyncio
async def test_metrics_empty_database():
    """Test metrics with empty database"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        metrics = await get_metrics(session)

        assert metrics.total_requirements == 0
        assert metrics.total_test_cases == 0
        assert metrics.total_links == 0
        assert metrics.total_suggestions == 0
        assert metrics.coverage_percentage == 0.0
        assert metrics.suggestion_acceptance_rate == 0.0
        assert metrics.manual_links == 0
        assert metrics.ai_suggested_links == 0

        # All algorithms should have zero metrics
        for algo in metrics.algorithm_breakdown:
            assert algo.total_suggestions == 0
            assert algo.acceptance_rate == 0.0

    await engine.dispose()


@pytest.mark.asyncio
async def test_traceability_matrix_linked_test_case_details():
    """Test that linked test case details are correctly populated"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        matrix = await get_traceability_matrix(session)

        # Find REQ-001
        req_coverage = next(item for item in matrix.matrix if item.external_id == "REQ-001")

        linked_tc = req_coverage.linked_test_cases[0]
        assert linked_tc.title == "Test Login Functionality"
        assert linked_tc.link_type == "covers"
        assert linked_tc.link_status == "accepted"
        assert linked_tc.confidence_score is None  # Manual link has no confidence score

        # Find REQ-002
        req_coverage = next(item for item in matrix.matrix if item.external_id == "REQ-002")

        linked_tc = req_coverage.linked_test_cases[0]
        assert linked_tc.title == "Test Data Export CSV"
        assert linked_tc.link_type == "covers"
        assert linked_tc.link_status == "pending"
        assert linked_tc.confidence_score == 0.85

    await engine.dispose()
