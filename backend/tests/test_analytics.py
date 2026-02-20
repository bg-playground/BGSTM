"""Tests for SuggestionAnalytics service"""

import uuid
from datetime import datetime, timedelta

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.base import Base
from app.models.requirement import PriorityLevel, Requirement, RequirementStatus, RequirementType
from app.models.suggestion import LinkSuggestion, SuggestionMethod, SuggestionStatus
from app.models.test_case import AutomationStatus, TestCase, TestCaseStatus, TestCaseType
from app.services.analytics import SuggestionAnalytics


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _make_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


def _req():
    return Requirement(
        id=uuid.uuid4(),
        external_id=f"REQ-{uuid.uuid4().hex[:6]}",
        title="Sample Requirement",
        description="Sample description",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=RequirementStatus.APPROVED,
    )


def _tc():
    return TestCase(
        id=uuid.uuid4(),
        external_id=f"TC-{uuid.uuid4().hex[:6]}",
        title="Sample Test Case",
        description="Sample description",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )


async def create_sample_data(session: AsyncSession):
    """Create a fixed set of suggestions for testing."""
    req = _req()
    tc = _tc()
    session.add_all([req, tc])
    await session.flush()

    now = datetime.utcnow()

    suggestions = [
        # ACCEPTED – hybrid, reviewed quickly
        LinkSuggestion(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=0.95,
            suggestion_method=SuggestionMethod.HYBRID,
            status=SuggestionStatus.ACCEPTED,
            created_at=now - timedelta(days=5),
            reviewed_at=now - timedelta(days=4),
            reviewed_by="alice",
        ),
        # ACCEPTED – keyword
        LinkSuggestion(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=0.80,
            suggestion_method=SuggestionMethod.KEYWORD_MATCH,
            status=SuggestionStatus.ACCEPTED,
            created_at=now - timedelta(days=10),
            reviewed_at=now - timedelta(days=9),
            reviewed_by="bob",
        ),
        # REJECTED – semantic
        LinkSuggestion(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=0.55,
            suggestion_method=SuggestionMethod.SEMANTIC_SIMILARITY,
            status=SuggestionStatus.REJECTED,
            created_at=now - timedelta(days=3),
            reviewed_at=now - timedelta(days=2),
            reviewed_by="alice",
        ),
        # PENDING – hybrid
        LinkSuggestion(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=0.70,
            suggestion_method=SuggestionMethod.HYBRID,
            status=SuggestionStatus.PENDING,
            created_at=now - timedelta(days=1),
        ),
    ]

    session.add_all(suggestions)
    await session.commit()


# ---------------------------------------------------------------------------
# get_acceptance_rates
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_acceptance_rates_basic():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        result = await SuggestionAnalytics.get_acceptance_rates(session)

    await engine.dispose()

    assert result["total"] == 4
    assert result["accepted"] == 2
    assert result["rejected"] == 1
    assert result["pending"] == 1
    assert result["acceptance_rate"] == 50.0
    assert result["rejection_rate"] == 25.0
    assert result["pending_rate"] == 25.0


@pytest.mark.asyncio
async def test_acceptance_rates_empty():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        result = await SuggestionAnalytics.get_acceptance_rates(session)

    await engine.dispose()

    assert result["total"] == 0
    assert result["acceptance_rate"] == 0.0
    assert result["rejection_rate"] == 0.0
    assert result["pending_rate"] == 0.0


@pytest.mark.asyncio
async def test_acceptance_rates_time_period_filter():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Only include suggestions from the last 4 days (should exclude days -5 and -10)
    cutoff = (datetime.utcnow() - timedelta(days=4)).isoformat()

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        result = await SuggestionAnalytics.get_acceptance_rates(session, time_period=cutoff)

    await engine.dispose()

    # Within last 4 days: the rejected one (-3 days) and the pending one (-1 day)
    assert result["total"] == 2
    assert result["rejected"] == 1
    assert result["pending"] == 1
    assert result["accepted"] == 0


# ---------------------------------------------------------------------------
# get_confidence_distribution
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_confidence_distribution_basic():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        result = await SuggestionAnalytics.get_confidence_distribution(session)

    await engine.dispose()

    assert result["total"] == 4
    assert len(result["buckets"]) == 10
    # scores: 0.95, 0.80, 0.55, 0.70
    assert result["average"] == pytest.approx((0.95 + 0.80 + 0.55 + 0.70) / 4, rel=1e-3)
    assert result["min"] == pytest.approx(0.55, rel=1e-3)
    assert result["max"] == pytest.approx(0.95, rel=1e-3)

    # bucket 0.9-1.0 should have count 1 (0.95)
    bucket_map = {b["range"]: b["count"] for b in result["buckets"]}
    assert bucket_map["0.9-1.0"] == 1
    # bucket 0.5-0.6 should have count 1 (0.55)
    assert bucket_map["0.5-0.6"] == 1


@pytest.mark.asyncio
async def test_confidence_distribution_algorithm_filter():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        result = await SuggestionAnalytics.get_confidence_distribution(session, algorithm="hybrid")

    await engine.dispose()

    # hybrid has scores 0.95 and 0.70
    assert result["total"] == 2
    assert result["min"] == pytest.approx(0.70, rel=1e-3)
    assert result["max"] == pytest.approx(0.95, rel=1e-3)


@pytest.mark.asyncio
async def test_confidence_distribution_empty():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        result = await SuggestionAnalytics.get_confidence_distribution(session)

    await engine.dispose()

    assert result["total"] == 0
    assert result["average"] == 0.0
    assert result["min"] == 0.0
    assert result["max"] == 0.0
    assert all(b["count"] == 0 for b in result["buckets"])


# ---------------------------------------------------------------------------
# get_generation_trends
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generation_trends_basic():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        result = await SuggestionAnalytics.get_generation_trends(session, days=30)

    await engine.dispose()

    assert result["days"] == 30
    assert result["total"] == 4
    assert len(result["daily"]) == 30
    # All daily entries must have a date and count key
    for entry in result["daily"]:
        assert "date" in entry
        assert "count" in entry


@pytest.mark.asyncio
async def test_generation_trends_empty():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        result = await SuggestionAnalytics.get_generation_trends(session, days=7)

    await engine.dispose()

    assert result["total"] == 0
    assert len(result["daily"]) == 7
    assert all(e["count"] == 0 for e in result["daily"])


@pytest.mark.asyncio
async def test_generation_trends_days_parameter():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        result = await SuggestionAnalytics.get_generation_trends(session, days=2)

    await engine.dispose()

    # Only the -1 day suggestion falls within last 2 days
    assert result["days"] == 2
    assert result["total"] == 1
    assert len(result["daily"]) == 2


# ---------------------------------------------------------------------------
# get_review_velocity
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_review_velocity_basic():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        result = await SuggestionAnalytics.get_review_velocity(session, days=30)

    await engine.dispose()

    # 3 suggestions reviewed within 30 days (accepted hybrid, accepted keyword, rejected semantic)
    assert result["reviewed_count"] == 3
    assert result["average_hours"] > 0
    assert result["min_hours"] > 0
    assert result["max_hours"] >= result["min_hours"]


@pytest.mark.asyncio
async def test_review_velocity_empty():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        result = await SuggestionAnalytics.get_review_velocity(session)

    await engine.dispose()

    assert result["reviewed_count"] == 0
    assert result["average_hours"] == 0.0
    assert result["min_hours"] == 0.0
    assert result["max_hours"] == 0.0


@pytest.mark.asyncio
async def test_review_velocity_days_filter():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        # Only the rejected suggestion was reviewed within the last 3 days (-2 days)
        result = await SuggestionAnalytics.get_review_velocity(session, days=3)

    await engine.dispose()

    assert result["reviewed_count"] == 1


# ---------------------------------------------------------------------------
# get_algorithm_comparison
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_algorithm_comparison_basic():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_sample_data(session)
        result = await SuggestionAnalytics.get_algorithm_comparison(session)

    await engine.dispose()

    algo_map = {a["algorithm"]: a for a in result["algorithms"]}

    # hybrid: 2 suggestions (1 accepted, 1 pending)
    assert algo_map["hybrid"]["total"] == 2
    assert algo_map["hybrid"]["accepted"] == 1
    assert algo_map["hybrid"]["pending"] == 1
    assert algo_map["hybrid"]["acceptance_rate"] == 50.0

    # keyword_match: 1 suggestion (accepted)
    assert algo_map["keyword_match"]["total"] == 1
    assert algo_map["keyword_match"]["accepted"] == 1
    assert algo_map["keyword_match"]["acceptance_rate"] == 100.0

    # semantic_similarity: 1 suggestion (rejected)
    assert algo_map["semantic_similarity"]["total"] == 1
    assert algo_map["semantic_similarity"]["rejected"] == 1
    assert algo_map["semantic_similarity"]["acceptance_rate"] == 0.0

    # llm_embedding: 0 suggestions
    assert algo_map["llm_embedding"]["total"] == 0
    assert algo_map["llm_embedding"]["acceptance_rate"] == 0.0


@pytest.mark.asyncio
async def test_algorithm_comparison_empty():
    engine = await _make_engine()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        result = await SuggestionAnalytics.get_algorithm_comparison(session)

    await engine.dispose()

    for algo in result["algorithms"]:
        assert algo["total"] == 0
        assert algo["acceptance_rate"] == 0.0
        assert algo["average_score"] == 0.0
