"""Tests for CRUD operations in app/crud/link.py"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.crud.link import (
    bulk_review_suggestions,
    create_link,
    create_suggestion,
    delete_link,
    get_link,
    get_links,
    get_links_by_requirement,
    get_links_by_test_case,
    get_pending_suggestions,
    get_suggestion,
    get_suggestions,
    review_suggestion,
)
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
from app.schemas.link import LinkCreate, SuggestionCreate, SuggestionReview


async def _make_engine_and_session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, session_factory


async def _create_req_and_test_case(session: AsyncSession):
    req = Requirement(
        id=uuid.uuid4(),
        external_id="REQ-L01",
        title="Link Test Requirement",
        description="Requirement for link CRUD tests",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED,
    )
    tc = TestCase(
        id=uuid.uuid4(),
        external_id="TC-L01",
        title="Link Test Case",
        description="Test case for link CRUD tests",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )
    session.add_all([req, tc])
    await session.flush()
    return req, tc


# ── Link CRUD ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_link():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        link_data = LinkCreate(
            requirement_id=req.id,
            test_case_id=tc.id,
            link_type=LinkType.COVERS,
            link_source=LinkSource.MANUAL,
            created_by="tester",
        )
        link = await create_link(session, link_data)
        assert link.id is not None
        assert link.requirement_id == req.id
        assert link.test_case_id == tc.id
        assert link.link_type == LinkType.COVERS
        assert link.link_source == LinkSource.MANUAL
        assert link.created_by == "tester"
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_link():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        link_data = LinkCreate(
            requirement_id=req.id,
            test_case_id=tc.id,
            link_type=LinkType.VERIFIES,
            link_source=LinkSource.AI_CONFIRMED,
        )
        created = await create_link(session, link_data)
        fetched = await get_link(session, created.id)
        assert fetched is not None
        assert fetched.id == created.id
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_link_not_found():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        result = await get_link(session, uuid.uuid4())
        assert result is None
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_links_pagination():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req = Requirement(
            id=uuid.uuid4(),
            external_id="REQ-P01",
            title="Pagination Req",
            description="For pagination test",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.MEDIUM,
            status=RequirementStatus.APPROVED,
        )
        session.add(req)
        await session.flush()

        # Create 3 test cases and links
        tc_ids = []
        for i in range(3):
            tc = TestCase(
                id=uuid.uuid4(),
                external_id=f"TC-P0{i}",
                title=f"Pagination TC {i}",
                description="Pagination test case",
                type=TestCaseType.FUNCTIONAL,
                priority=PriorityLevel.LOW,
                status=TestCaseStatus.DRAFT,
                automation_status=AutomationStatus.MANUAL,
            )
            session.add(tc)
            await session.flush()
            tc_ids.append(tc.id)

        for tc_id in tc_ids:
            link = RequirementTestCaseLink(
                id=uuid.uuid4(),
                requirement_id=req.id,
                test_case_id=tc_id,
                link_type=LinkType.COVERS,
                link_source=LinkSource.MANUAL,
            )
            session.add(link)
        await session.commit()

        all_links = await get_links(session, skip=0, limit=100)
        assert len(all_links) == 3

        first_page = await get_links(session, skip=0, limit=2)
        assert len(first_page) == 2

        second_page = await get_links(session, skip=2, limit=2)
        assert len(second_page) == 1
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_links_by_requirement():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req1 = Requirement(
            id=uuid.uuid4(),
            external_id="REQ-R01",
            title="Req 1",
            description="First requirement",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=RequirementStatus.APPROVED,
        )
        req2 = Requirement(
            id=uuid.uuid4(),
            external_id="REQ-R02",
            title="Req 2",
            description="Second requirement",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.LOW,
            status=RequirementStatus.DRAFT,
        )
        tc = TestCase(
            id=uuid.uuid4(),
            external_id="TC-R01",
            title="Shared TC",
            description="Shared test case",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=TestCaseStatus.READY,
            automation_status=AutomationStatus.MANUAL,
        )
        session.add_all([req1, req2, tc])
        await session.flush()

        link1 = RequirementTestCaseLink(
            id=uuid.uuid4(),
            requirement_id=req1.id,
            test_case_id=tc.id,
            link_type=LinkType.COVERS,
            link_source=LinkSource.MANUAL,
        )
        session.add(link1)
        await session.commit()

        links_req1 = await get_links_by_requirement(session, req1.id)
        links_req2 = await get_links_by_requirement(session, req2.id)

        assert len(links_req1) == 1
        assert links_req1[0].requirement_id == req1.id
        assert len(links_req2) == 0
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_links_by_test_case():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req = Requirement(
            id=uuid.uuid4(),
            external_id="REQ-TC01",
            title="Req for TC filter",
            description="Requirement for test case filter test",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=RequirementStatus.APPROVED,
        )
        tc1 = TestCase(
            id=uuid.uuid4(),
            external_id="TC-TC01",
            title="TC with link",
            description="Test case with a link",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.HIGH,
            status=TestCaseStatus.READY,
            automation_status=AutomationStatus.MANUAL,
        )
        tc2 = TestCase(
            id=uuid.uuid4(),
            external_id="TC-TC02",
            title="TC without link",
            description="Test case without any link",
            type=TestCaseType.FUNCTIONAL,
            priority=PriorityLevel.LOW,
            status=TestCaseStatus.DRAFT,
            automation_status=AutomationStatus.MANUAL,
        )
        session.add_all([req, tc1, tc2])
        await session.flush()

        link = RequirementTestCaseLink(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc1.id,
            link_type=LinkType.COVERS,
            link_source=LinkSource.MANUAL,
        )
        session.add(link)
        await session.commit()

        links_tc1 = await get_links_by_test_case(session, tc1.id)
        links_tc2 = await get_links_by_test_case(session, tc2.id)

        assert len(links_tc1) == 1
        assert links_tc1[0].test_case_id == tc1.id
        assert len(links_tc2) == 0
    await engine.dispose()


@pytest.mark.asyncio
async def test_delete_link():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        link_data = LinkCreate(
            requirement_id=req.id,
            test_case_id=tc.id,
            link_type=LinkType.COVERS,
            link_source=LinkSource.MANUAL,
        )
        created = await create_link(session, link_data)
        link_id = created.id

        result = await delete_link(session, link_id)
        assert result is True

        fetched = await get_link(session, link_id)
        assert fetched is None
    await engine.dispose()


@pytest.mark.asyncio
async def test_delete_link_not_found():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        result = await delete_link(session, uuid.uuid4())
        assert result is False
    await engine.dispose()


# ── Suggestion CRUD ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_suggestion():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        sugg_data = SuggestionCreate(
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=0.85,
            suggestion_method=SuggestionMethod.HYBRID,
            suggestion_reason="High keyword overlap",
        )
        suggestion = await create_suggestion(session, sugg_data)
        assert suggestion.id is not None
        assert suggestion.requirement_id == req.id
        assert suggestion.test_case_id == tc.id
        assert suggestion.similarity_score == pytest.approx(0.85)
        assert suggestion.suggestion_method == SuggestionMethod.HYBRID
        assert suggestion.status == SuggestionStatus.PENDING
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_suggestion():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        sugg_data = SuggestionCreate(
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=0.70,
            suggestion_method=SuggestionMethod.KEYWORD_MATCH,
        )
        created = await create_suggestion(session, sugg_data)
        fetched = await get_suggestion(session, created.id)
        assert fetched is not None
        assert fetched.id == created.id
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_suggestion_not_found():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        result = await get_suggestion(session, uuid.uuid4())
        assert result is None
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_suggestions_all():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        for score in [0.9, 0.7, 0.5]:
            sugg = LinkSuggestion(
                id=uuid.uuid4(),
                requirement_id=req.id,
                test_case_id=tc.id,
                similarity_score=score,
                suggestion_method=SuggestionMethod.SEMANTIC_SIMILARITY,
                status=SuggestionStatus.PENDING,
            )
            session.add(sugg)
        await session.commit()

        suggestions = await get_suggestions(session, skip=0, limit=100)
        assert len(suggestions) == 3

        limited = await get_suggestions(session, skip=0, limit=2)
        assert len(limited) == 2
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_pending_suggestions_no_filters():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
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
            similarity_score=0.90,
            suggestion_method=SuggestionMethod.HYBRID,
            status=SuggestionStatus.ACCEPTED,
        )
        session.add_all([pending, accepted])
        await session.commit()

        results = await get_pending_suggestions(session)
        assert len(results) == 1
        assert results[0].status == SuggestionStatus.PENDING
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_pending_suggestions_min_score_filter():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        for score in [0.9, 0.6, 0.4]:
            sugg = LinkSuggestion(
                id=uuid.uuid4(),
                requirement_id=req.id,
                test_case_id=tc.id,
                similarity_score=score,
                suggestion_method=SuggestionMethod.KEYWORD_MATCH,
                status=SuggestionStatus.PENDING,
            )
            session.add(sugg)
        await session.commit()

        high_quality = await get_pending_suggestions(session, min_score=0.7)
        assert len(high_quality) == 1
        assert high_quality[0].similarity_score == pytest.approx(0.9)
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_pending_suggestions_max_score_filter():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        for score in [0.9, 0.6, 0.4]:
            sugg = LinkSuggestion(
                id=uuid.uuid4(),
                requirement_id=req.id,
                test_case_id=tc.id,
                similarity_score=score,
                suggestion_method=SuggestionMethod.KEYWORD_MATCH,
                status=SuggestionStatus.PENDING,
            )
            session.add(sugg)
        await session.commit()

        low_quality = await get_pending_suggestions(session, max_score=0.65)
        scores = {s.similarity_score for s in low_quality}
        assert all(s <= 0.65 for s in scores)
        assert len(low_quality) == 2
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_pending_suggestions_algorithm_filter():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        hybrid_sugg = LinkSuggestion(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=0.80,
            suggestion_method=SuggestionMethod.HYBRID,
            status=SuggestionStatus.PENDING,
        )
        keyword_sugg = LinkSuggestion(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=0.70,
            suggestion_method=SuggestionMethod.KEYWORD_MATCH,
            status=SuggestionStatus.PENDING,
        )
        session.add_all([hybrid_sugg, keyword_sugg])
        await session.commit()

        hybrid_results = await get_pending_suggestions(session, algorithm="hybrid")
        assert len(hybrid_results) == 1
        assert hybrid_results[0].suggestion_method == SuggestionMethod.HYBRID

        keyword_results = await get_pending_suggestions(session, algorithm="keyword")
        assert len(keyword_results) == 1
        assert keyword_results[0].suggestion_method == SuggestionMethod.KEYWORD_MATCH
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_pending_suggestions_sort_by_score_desc():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        for score in [0.5, 0.9, 0.7]:
            sugg = LinkSuggestion(
                id=uuid.uuid4(),
                requirement_id=req.id,
                test_case_id=tc.id,
                similarity_score=score,
                suggestion_method=SuggestionMethod.HYBRID,
                status=SuggestionStatus.PENDING,
            )
            session.add(sugg)
        await session.commit()

        results = await get_pending_suggestions(session, sort_by="score", sort_order="desc")
        scores = [s.similarity_score for s in results]
        assert scores == sorted(scores, reverse=True)
    await engine.dispose()


@pytest.mark.asyncio
async def test_get_pending_suggestions_sort_by_score_asc():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        for score in [0.5, 0.9, 0.7]:
            sugg = LinkSuggestion(
                id=uuid.uuid4(),
                requirement_id=req.id,
                test_case_id=tc.id,
                similarity_score=score,
                suggestion_method=SuggestionMethod.HYBRID,
                status=SuggestionStatus.PENDING,
            )
            session.add(sugg)
        await session.commit()

        results = await get_pending_suggestions(session, sort_by="score", sort_order="asc")
        scores = [s.similarity_score for s in results]
        assert scores == sorted(scores)
    await engine.dispose()


@pytest.mark.asyncio
async def test_review_suggestion_accept():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        sugg_data = SuggestionCreate(
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=0.88,
            suggestion_method=SuggestionMethod.HYBRID,
        )
        created = await create_suggestion(session, sugg_data)

        review = SuggestionReview(
            status=SuggestionStatus.ACCEPTED,
            feedback="Looks good",
            reviewed_by="reviewer@example.com",
        )
        reviewed = await review_suggestion(session, created.id, review)

        assert reviewed is not None
        assert reviewed.status == SuggestionStatus.ACCEPTED
        assert reviewed.feedback == "Looks good"
        assert reviewed.reviewed_by == "reviewer@example.com"
        assert reviewed.reviewed_at is not None
    await engine.dispose()


@pytest.mark.asyncio
async def test_review_suggestion_reject():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        sugg_data = SuggestionCreate(
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=0.55,
            suggestion_method=SuggestionMethod.KEYWORD_MATCH,
        )
        created = await create_suggestion(session, sugg_data)

        review = SuggestionReview(status=SuggestionStatus.REJECTED)
        reviewed = await review_suggestion(session, created.id, review)

        assert reviewed is not None
        assert reviewed.status == SuggestionStatus.REJECTED
    await engine.dispose()


@pytest.mark.asyncio
async def test_review_suggestion_not_found():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        review = SuggestionReview(status=SuggestionStatus.ACCEPTED)
        result = await review_suggestion(session, uuid.uuid4(), review)
        assert result is None
    await engine.dispose()


@pytest.mark.asyncio
async def test_bulk_review_suggestions():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        sugg_ids = []
        for score in [0.8, 0.7, 0.6]:
            sugg = LinkSuggestion(
                id=uuid.uuid4(),
                requirement_id=req.id,
                test_case_id=tc.id,
                similarity_score=score,
                suggestion_method=SuggestionMethod.HYBRID,
                status=SuggestionStatus.PENDING,
            )
            session.add(sugg)
            sugg_ids.append(sugg.id)
        await session.commit()

        count = await bulk_review_suggestions(
            session, sugg_ids[:2], SuggestionStatus.ACCEPTED, feedback="bulk accept", reviewed_by="admin"
        )
        assert count == 2

        for sugg_id in sugg_ids[:2]:
            s = await get_suggestion(session, sugg_id)
            assert s.status == SuggestionStatus.ACCEPTED
            assert s.feedback == "bulk accept"
            assert s.reviewed_by == "admin"

        s3 = await get_suggestion(session, sugg_ids[2])
        assert s3.status == SuggestionStatus.PENDING
    await engine.dispose()


@pytest.mark.asyncio
async def test_bulk_review_skips_non_pending():
    engine, factory = await _make_engine_and_session_factory()
    async with factory() as session:
        req, tc = await _create_req_and_test_case(session)
        already_accepted = LinkSuggestion(
            id=uuid.uuid4(),
            requirement_id=req.id,
            test_case_id=tc.id,
            similarity_score=0.9,
            suggestion_method=SuggestionMethod.HYBRID,
            status=SuggestionStatus.ACCEPTED,
        )
        session.add(already_accepted)
        await session.commit()

        count = await bulk_review_suggestions(session, [already_accepted.id], SuggestionStatus.REJECTED)
        # Already-accepted suggestion should not be updated
        assert count == 0

        s = await get_suggestion(session, already_accepted.id)
        assert s.status == SuggestionStatus.ACCEPTED
    await engine.dispose()
