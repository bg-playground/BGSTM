"""Tests for suggestion engine performance optimizations"""

import uuid
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.ai_suggestions.config import SuggestionConfig
from app.ai_suggestions.engine import SuggestionEngine
from app.models.base import Base
from app.models.link import LinkSource, LinkType, RequirementTestCaseLink
from app.models.requirement import (
    PriorityLevel,
    Requirement,
    RequirementStatus,
    RequirementType,
)
from app.models.suggestion import LinkSuggestion
from app.models.test_case import (
    AutomationStatus,
    TestCase,
    TestCaseStatus,
    TestCaseType,
)


async def _make_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine


def _req(i: int) -> Requirement:
    return Requirement(
        id=uuid.uuid4(),
        external_id=f"REQ-{i:03d}",
        title=f"User Authentication {i}",
        description=f"The system shall allow users to login {i}",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED,
    )


def _tc(i: int) -> TestCase:
    return TestCase(
        id=uuid.uuid4(),
        external_id=f"TC-{i:03d}",
        title=f"Test User Login {i}",
        description=f"Verify that users can login {i}",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.AUTOMATED,
    )


@pytest.mark.asyncio
async def test_batch_suggestion_creation():
    """Test that batch suggestion creation saves all suggestions correctly"""
    engine = await _make_db()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create enough items to trigger multiple batches (BATCH_SIZE=100)
    num_reqs = 8
    num_tcs = 8  # 64 pairs, will be batched

    async with AsyncSessionLocal() as session:
        reqs = [_req(i) for i in range(num_reqs)]
        tcs = [_tc(i) for i in range(num_tcs)]
        session.add_all(reqs + tcs)
        await session.commit()

        config = SuggestionConfig(default_algorithm="keyword", min_confidence_threshold=0.0)
        sug_engine = SuggestionEngine(config=config)

        result = await sug_engine.generate_suggestions(session)

        # All pairs should be analyzed
        assert result["pairs_analyzed"] == num_reqs * num_tcs

        # Verify suggestions are saved in DB
        db_count = await session.execute(select(LinkSuggestion))
        saved = list(db_count.scalars().all())
        assert len(saved) == result["suggestions_created"]

    await engine.dispose()


@pytest.mark.asyncio
async def test_batch_suggestion_creation_large():
    """Test batch with more than BATCH_SIZE suggestions triggers flush mid-loop"""
    engine = await _make_db()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # 11 x 11 = 121 pairs > BATCH_SIZE(100), forces at least one mid-loop flush
    num_reqs = 11
    num_tcs = 11

    async with AsyncSessionLocal() as session:
        reqs = [_req(i) for i in range(num_reqs)]
        tcs = [_tc(i) for i in range(num_tcs)]
        session.add_all(reqs + tcs)
        await session.commit()

        config = SuggestionConfig(default_algorithm="keyword", min_confidence_threshold=0.0)
        sug_engine = SuggestionEngine(config=config)

        result = await sug_engine.generate_suggestions(session)

        assert result["pairs_analyzed"] == num_reqs * num_tcs

        # All created suggestions should be persisted
        db_result = await session.execute(select(LinkSuggestion))
        saved = list(db_result.scalars().all())
        assert len(saved) == result["suggestions_created"]

    await engine.dispose()


@pytest.mark.asyncio
async def test_precomputed_text_called_once_per_item():
    """Test that _combine_text and _combine_test_case_text are called once per item, not per pair"""
    engine = await _make_db()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    num_reqs = 3
    num_tcs = 4

    async with AsyncSessionLocal() as session:
        reqs = [_req(i) for i in range(num_reqs)]
        tcs = [_tc(i) for i in range(num_tcs)]
        session.add_all(reqs + tcs)
        await session.commit()

        config = SuggestionConfig(default_algorithm="keyword", min_confidence_threshold=0.0)
        sug_engine = SuggestionEngine(config=config)

        with (
            patch.object(sug_engine, "_combine_text", wraps=sug_engine._combine_text) as mock_req_text,
            patch.object(
                sug_engine, "_combine_test_case_text", wraps=sug_engine._combine_test_case_text
            ) as mock_tc_text,
        ):
            await sug_engine.generate_suggestions(session)

        # Each should be called exactly once per item (for pre-computation), not per pair
        assert mock_req_text.call_count == num_reqs
        assert mock_tc_text.call_count == num_tcs

    await engine.dispose()


@pytest.mark.asyncio
async def test_incremental_generation_with_requirement_ids():
    """Test incremental generation with specific requirement_ids"""
    engine = await _make_db()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        reqs = [_req(i) for i in range(3)]
        tcs = [_tc(i) for i in range(3)]
        session.add_all(reqs + tcs)
        await session.commit()

        config = SuggestionConfig(default_algorithm="keyword", min_confidence_threshold=0.0)
        sug_engine = SuggestionEngine(config=config)

        # Only generate for the first requirement
        result = await sug_engine.generate_suggestions(session, requirement_ids=[reqs[0].id])

        # Should only analyze 1 requirement × 3 test cases
        assert result["pairs_analyzed"] == 3

        # Only suggestions for reqs[0] should exist
        db_result = await session.execute(select(LinkSuggestion).where(LinkSuggestion.requirement_id == reqs[0].id))
        req0_suggestions = list(db_result.scalars().all())

        db_result2 = await session.execute(select(LinkSuggestion).where(LinkSuggestion.requirement_id != reqs[0].id))
        other_suggestions = list(db_result2.scalars().all())

        assert len(req0_suggestions) == result["suggestions_created"]
        assert len(other_suggestions) == 0

    await engine.dispose()


@pytest.mark.asyncio
async def test_scoped_dedup_checking():
    """Test that dedup checking is scoped to requirement_ids when provided"""
    engine = await _make_db()
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        reqs = [_req(i) for i in range(2)]
        tcs = [_tc(i) for i in range(2)]
        session.add_all(reqs + tcs)
        # Add an existing link for reqs[0] -> tcs[0]
        link = RequirementTestCaseLink(
            id=uuid.uuid4(),
            requirement_id=reqs[0].id,
            test_case_id=tcs[0].id,
            link_type=LinkType.COVERS,
            link_source=LinkSource.MANUAL,
        )
        session.add(link)
        await session.commit()

        config = SuggestionConfig(default_algorithm="keyword", min_confidence_threshold=0.0)
        sug_engine = SuggestionEngine(config=config)

        # Generate only for reqs[0]
        result = await sug_engine.generate_suggestions(session, requirement_ids=[reqs[0].id])

        # The existing link pair should be skipped
        assert result["suggestions_skipped"] >= 1
        # Should still analyze 2 pairs (reqs[0] × 2 tcs)
        assert result["pairs_analyzed"] == 2

    await engine.dispose()
