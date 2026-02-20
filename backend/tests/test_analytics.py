"""Tests for SuggestionAnalytics service"""

import uuid
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base
from app.models.requirement import PriorityLevel, Requirement, RequirementStatus, RequirementType
from app.models.suggestion import LinkSuggestion, SuggestionMethod, SuggestionStatus
from app.models.test_case import AutomationStatus, TestCase, TestCaseStatus, TestCaseType
from app.services.analytics import SuggestionAnalytics


async def create_analytics_sample_data(session: AsyncSession):
    """Create sample requirements, test cases, and suggestions for analytics tests"""
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
        title="Test Login",
        description="Test user login",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.AUTOMATED,
    )
    tc2 = TestCase(
        id=uuid.uuid4(),
        external_id="TC-002",
        title="Test Export",
        description="Test data export",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )
    tc3 = TestCase(
        id=uuid.uuid4(),
        external_id="TC-003",
        title="Test Performance",
        description="Test performance",
        type=TestCaseType.PERFORMANCE,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.AUTOMATED,
    )

    session.add_all([req1, req2, tc1, tc2, tc3])
    await session.flush()

    now = datetime(2024, 6, 15, 12, 0, 0)
    reviewed_fast = datetime(2024, 6, 15, 14, 0, 0)  # 2 hours later
    reviewed_slow = datetime(2024, 6, 16, 12, 0, 0)  # 24 hours later

    sugg1 = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req1.id,
        test_case_id=tc1.id,
        similarity_score=0.92,
        suggestion_method=SuggestionMethod.HYBRID,
        status=SuggestionStatus.ACCEPTED,
        created_at=now,
        reviewed_at=reviewed_fast,
        reviewed_by="user1",
    )
    sugg2 = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req1.id,
        test_case_id=tc2.id,
        similarity_score=0.75,
        suggestion_method=SuggestionMethod.KEYWORD_MATCH,
        status=SuggestionStatus.PENDING,
        created_at=now,
    )
    sugg3 = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req2.id,
        test_case_id=tc3.id,
        similarity_score=0.55,
        suggestion_method=SuggestionMethod.SEMANTIC_SIMILARITY,
        status=SuggestionStatus.REJECTED,
        created_at=now,
        reviewed_at=reviewed_slow,
        reviewed_by="user2",
    )
    sugg4 = LinkSuggestion(
        id=uuid.uuid4(),
        requirement_id=req2.id,
        test_case_id=tc1.id,
        similarity_score=0.88,
        suggestion_method=SuggestionMethod.HYBRID,
        status=SuggestionStatus.ACCEPTED,
        created_at=now,
        reviewed_at=reviewed_fast,
        reviewed_by="user1",
    )

    session.add_all([sugg1, sugg2, sugg3, sugg4])
    await session.commit()


@pytest.mark.asyncio
async def test_acceptance_rates_basic():
    """Test acceptance rates returns correct monthly breakdown"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_analytics_sample_data(session)
        analytics = SuggestionAnalytics(session)
        rates = await analytics.get_acceptance_rates()

        assert len(rates) == 1  # All in same month (2024-06)
        rate = rates[0]
        assert rate["period"] == "2024-06"
        assert rate["total"] == 4
        assert rate["accepted"] == 2
        assert rate["rejected"] == 1
        assert rate["pending"] == 1
        assert rate["acceptance_rate"] == 50.0

    await engine.dispose()


@pytest.mark.asyncio
async def test_acceptance_rates_empty():
    """Test acceptance rates with no suggestions"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        analytics = SuggestionAnalytics(session)
        rates = await analytics.get_acceptance_rates()
        assert rates == []

    await engine.dispose()


@pytest.mark.asyncio
async def test_confidence_distribution_basic():
    """Test confidence distribution bins are correct"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_analytics_sample_data(session)
        analytics = SuggestionAnalytics(session)
        dist = await analytics.get_confidence_distribution()

        assert len(dist) == 5  # 5 bins

        # Map by range label
        by_range = {d["range"]: d for d in dist}

        # Scores: 0.92, 0.75, 0.55, 0.88
        # 0.4-0.6: 0.55 → 1
        # 0.6-0.8: 0.75 → 1
        # 0.8-1.0: 0.92, 0.88 → 2
        assert by_range["0.4-0.6"]["count"] == 1
        assert by_range["0.6-0.8"]["count"] == 1
        assert by_range["0.8-1.0"]["count"] == 2
        assert by_range["0.0-0.2"]["count"] == 0
        assert by_range["0.2-0.4"]["count"] == 0

        # Percentages should sum to 100% (for 4 suggestions)
        total_pct = sum(d["percentage"] for d in dist)
        assert total_pct == pytest.approx(100.0, rel=0.01)

    await engine.dispose()


@pytest.mark.asyncio
async def test_confidence_distribution_empty():
    """Test confidence distribution with no suggestions"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        analytics = SuggestionAnalytics(session)
        dist = await analytics.get_confidence_distribution()
        assert len(dist) == 5
        for d in dist:
            assert d["count"] == 0
            assert d["percentage"] == 0.0

    await engine.dispose()


@pytest.mark.asyncio
async def test_generation_trends_basic():
    """Test generation trends returns monthly counts"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_analytics_sample_data(session)
        analytics = SuggestionAnalytics(session)
        trends = await analytics.get_generation_trends()

        assert len(trends) == 1
        assert trends[0]["period"] == "2024-06"
        assert trends[0]["count"] == 4

    await engine.dispose()


@pytest.mark.asyncio
async def test_generation_trends_empty():
    """Test generation trends with no suggestions"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        analytics = SuggestionAnalytics(session)
        trends = await analytics.get_generation_trends()
        assert trends == []

    await engine.dispose()


@pytest.mark.asyncio
async def test_review_velocity_basic():
    """Test review velocity calculates correct average and median"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_analytics_sample_data(session)
        analytics = SuggestionAnalytics(session)
        velocity = await analytics.get_review_velocity()

        # 3 suggestions have reviewed_at: sugg1 (2h), sugg3 (24h), sugg4 (2h)
        assert velocity["total_reviewed"] == 3
        # Average: (2 + 24 + 2) / 3 = 9.33 hours
        assert velocity["average_hours"] == pytest.approx(9.33, rel=0.01)
        # Median: sorted [2, 2, 24] → middle = 2
        assert velocity["median_hours"] == pytest.approx(2.0, rel=0.01)

    await engine.dispose()


@pytest.mark.asyncio
async def test_review_velocity_empty():
    """Test review velocity with no reviewed suggestions"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        analytics = SuggestionAnalytics(session)
        velocity = await analytics.get_review_velocity()
        assert velocity["total_reviewed"] == 0
        assert velocity["average_hours"] == 0.0
        assert velocity["median_hours"] == 0.0

    await engine.dispose()


@pytest.mark.asyncio
async def test_algorithm_comparison_basic():
    """Test algorithm comparison returns correct per-algorithm metrics"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_analytics_sample_data(session)
        analytics = SuggestionAnalytics(session)
        comparison = await analytics.get_algorithm_comparison()

        # All SuggestionMethod values should be present
        algorithms = {item["algorithm"] for item in comparison}
        assert "hybrid" in algorithms
        assert "keyword_match" in algorithms
        assert "semantic_similarity" in algorithms

        by_algo = {item["algorithm"]: item for item in comparison}

        # Hybrid: 2 suggestions (sugg1 score=0.92, sugg4 score=0.88), both ACCEPTED
        hybrid = by_algo["hybrid"]
        assert hybrid["total"] == 2
        assert hybrid["accepted"] == 2
        assert hybrid["acceptance_rate"] == 100.0
        assert hybrid["avg_confidence"] == pytest.approx((0.92 + 0.88) / 2, rel=0.01)

        # Keyword: 1 suggestion (sugg2, PENDING)
        keyword = by_algo["keyword_match"]
        assert keyword["total"] == 1
        assert keyword["pending"] == 1
        assert keyword["acceptance_rate"] == 0.0

        # Semantic: 1 suggestion (sugg3, REJECTED)
        semantic = by_algo["semantic_similarity"]
        assert semantic["total"] == 1
        assert semantic["rejected"] == 1
        assert semantic["acceptance_rate"] == 0.0

    await engine.dispose()


@pytest.mark.asyncio
async def test_algorithm_comparison_empty():
    """Test algorithm comparison with no suggestions"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        analytics = SuggestionAnalytics(session)
        comparison = await analytics.get_algorithm_comparison()

        for item in comparison:
            assert item["total"] == 0
            assert item["acceptance_rate"] == 0.0
            assert item["avg_confidence"] == 0.0

    await engine.dispose()
