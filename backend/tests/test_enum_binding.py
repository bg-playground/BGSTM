"""Regression tests for SQLAlchemy enum binding.

Verifies that all model Enum columns use lowercase values (matching the
PostgreSQL enum types created by the Alembic migration) rather than
uppercase enum member names.
"""

import pytest
from sqlalchemy import Enum

from app.models.requirement import _enum_values


def _bind(enum_type: Enum, member):
    """Return the value that would be sent to the database."""
    bp = enum_type.bind_processor(None)
    return bp(member) if bp else str(member)


# ---------------------------------------------------------------------------
# Requirement enums
# ---------------------------------------------------------------------------


class TestRequirementEnumBinding:
    def test_requirement_type_values_are_lowercase(self):
        from app.models.requirement import RequirementType

        e = Enum(RequirementType, values_callable=_enum_values, name="t")
        assert _bind(e, RequirementType.FUNCTIONAL) == "functional"
        assert _bind(e, RequirementType.NON_FUNCTIONAL) == "non_functional"
        assert _bind(e, RequirementType.TECHNICAL) == "technical"

    def test_priority_level_values_are_lowercase(self):
        from app.models.requirement import PriorityLevel

        e = Enum(PriorityLevel, values_callable=_enum_values, name="t")
        assert _bind(e, PriorityLevel.CRITICAL) == "critical"
        assert _bind(e, PriorityLevel.HIGH) == "high"
        assert _bind(e, PriorityLevel.MEDIUM) == "medium"
        assert _bind(e, PriorityLevel.LOW) == "low"

    def test_requirement_status_values_are_lowercase(self):
        from app.models.requirement import RequirementStatus

        e = Enum(RequirementStatus, values_callable=_enum_values, name="t")
        assert _bind(e, RequirementStatus.DRAFT) == "draft"
        assert _bind(e, RequirementStatus.APPROVED) == "approved"


# ---------------------------------------------------------------------------
# Suggestion enums
# ---------------------------------------------------------------------------


class TestSuggestionEnumBinding:
    def test_suggestion_status_values_are_lowercase(self):
        from app.models.suggestion import SuggestionStatus

        e = Enum(SuggestionStatus, values_callable=_enum_values, name="t")
        assert _bind(e, SuggestionStatus.PENDING) == "pending"
        assert _bind(e, SuggestionStatus.ACCEPTED) == "accepted"
        assert _bind(e, SuggestionStatus.REJECTED) == "rejected"
        assert _bind(e, SuggestionStatus.EXPIRED) == "expired"

    def test_suggestion_method_values_are_lowercase(self):
        from app.models.suggestion import SuggestionMethod

        e = Enum(SuggestionMethod, values_callable=_enum_values, name="t")
        assert _bind(e, SuggestionMethod.SEMANTIC_SIMILARITY) == "semantic_similarity"
        assert _bind(e, SuggestionMethod.KEYWORD_MATCH) == "keyword_match"
        assert _bind(e, SuggestionMethod.HYBRID) == "hybrid"


# ---------------------------------------------------------------------------
# Link enums
# ---------------------------------------------------------------------------


class TestLinkEnumBinding:
    def test_link_type_values_are_lowercase(self):
        from app.models.link import LinkType

        e = Enum(LinkType, values_callable=_enum_values, name="t")
        assert _bind(e, LinkType.COVERS) == "covers"
        assert _bind(e, LinkType.VERIFIES) == "verifies"
        assert _bind(e, LinkType.VALIDATES) == "validates"
        assert _bind(e, LinkType.RELATED) == "related"

    def test_link_source_values_are_lowercase(self):
        from app.models.link import LinkSource

        e = Enum(LinkSource, values_callable=_enum_values, name="t")
        assert _bind(e, LinkSource.MANUAL) == "manual"
        assert _bind(e, LinkSource.AI_SUGGESTED) == "ai_suggested"
        assert _bind(e, LinkSource.AI_CONFIRMED) == "ai_confirmed"
        assert _bind(e, LinkSource.IMPORTED) == "imported"


# ---------------------------------------------------------------------------
# TestCase enums
# ---------------------------------------------------------------------------


class TestTestCaseEnumBinding:
    def test_test_case_type_values_are_lowercase(self):
        from app.models.test_case import TestCaseType

        e = Enum(TestCaseType, values_callable=_enum_values, name="t")
        assert _bind(e, TestCaseType.FUNCTIONAL) == "functional"
        assert _bind(e, TestCaseType.PERFORMANCE) == "performance"

    def test_test_case_status_values_are_lowercase(self):
        from app.models.test_case import TestCaseStatus

        e = Enum(TestCaseStatus, values_callable=_enum_values, name="t")
        assert _bind(e, TestCaseStatus.DRAFT) == "draft"
        assert _bind(e, TestCaseStatus.READY) == "ready"

    def test_automation_status_values_are_lowercase(self):
        from app.models.test_case import AutomationStatus

        e = Enum(AutomationStatus, values_callable=_enum_values, name="t")
        assert _bind(e, AutomationStatus.MANUAL) == "manual"
        assert _bind(e, AutomationStatus.AUTOMATED) == "automated"


# ---------------------------------------------------------------------------
# Notification enum
# ---------------------------------------------------------------------------


class TestNotificationEnumBinding:
    def test_notification_type_values_are_lowercase(self):
        from app.models.notification import NotificationType

        e = Enum(NotificationType, values_callable=_enum_values, name="t")
        assert _bind(e, NotificationType.REQUIREMENT_CREATED) == "requirement_created"
        assert _bind(e, NotificationType.SUGGESTIONS_GENERATED) == "suggestions_generated"
        assert _bind(e, NotificationType.SUGGESTION_REVIEWED) == "suggestion_reviewed"
        assert _bind(e, NotificationType.COVERAGE_DROP) == "coverage_drop"
        assert _bind(e, NotificationType.TEST_CASE_CREATED) == "test_case_created"


# ---------------------------------------------------------------------------
# Round-trip tests via SQLite (simulates PostgreSQL non-native enum)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_suggestion_status_roundtrip_via_sqlite():
    """Verify SuggestionStatus PENDING is stored and queried as lowercase 'pending'."""
    import uuid

    from sqlalchemy import select, text
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.models.base import Base
    from app.models.requirement import PriorityLevel, Requirement, RequirementStatus, RequirementType
    from app.models.suggestion import LinkSuggestion, SuggestionMethod, SuggestionStatus
    from app.models.test_case import AutomationStatus, TestCase, TestCaseStatus, TestCaseType

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    req_id = uuid.uuid4()
    tc_id = uuid.uuid4()

    async with AsyncSessionLocal() as session:
        session.add(
            Requirement(
                id=req_id,
                title="R",
                description="d",
                type=RequirementType.FUNCTIONAL,
                priority=PriorityLevel.HIGH,
                status=RequirementStatus.APPROVED,
            )
        )
        session.add(
            TestCase(
                id=tc_id,
                title="T",
                description="d",
                type=TestCaseType.FUNCTIONAL,
                priority=PriorityLevel.HIGH,
                status=TestCaseStatus.READY,
                automation_status=AutomationStatus.MANUAL,
            )
        )
        session.add(
            LinkSuggestion(
                id=uuid.uuid4(),
                requirement_id=req_id,
                test_case_id=tc_id,
                similarity_score=0.9,
                suggestion_method=SuggestionMethod.HYBRID,
                status=SuggestionStatus.PENDING,
            )
        )
        await session.commit()

        # The raw stored value must be lowercase 'pending'
        raw = await session.execute(text("SELECT status FROM link_suggestions LIMIT 1"))
        raw_value = raw.scalar()
        assert raw_value == "pending", f"Expected 'pending', got {raw_value!r}"

        # ORM query by enum comparison must work
        result = await session.execute(select(LinkSuggestion).where(LinkSuggestion.status == SuggestionStatus.PENDING))
        rows = result.scalars().all()
        assert len(rows) == 1
        assert rows[0].status == SuggestionStatus.PENDING

    await engine.dispose()


@pytest.mark.asyncio
async def test_requirement_type_roundtrip_via_sqlite():
    """Verify RequirementType FUNCTIONAL is stored and queried as lowercase 'functional'."""
    import uuid

    from sqlalchemy import select, text
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.models.base import Base
    from app.models.requirement import PriorityLevel, Requirement, RequirementStatus, RequirementType

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        session.add(
            Requirement(
                id=uuid.uuid4(),
                title="R",
                description="d",
                type=RequirementType.FUNCTIONAL,
                priority=PriorityLevel.HIGH,
                status=RequirementStatus.APPROVED,
            )
        )
        await session.commit()

        raw = await session.execute(text("SELECT type FROM requirements LIMIT 1"))
        raw_value = raw.scalar()
        assert raw_value == "functional", f"Expected 'functional', got {raw_value!r}"

        result = await session.execute(select(Requirement).where(Requirement.type == RequirementType.FUNCTIONAL))
        rows = result.scalars().all()
        assert len(rows) == 1
        assert rows[0].type == RequirementType.FUNCTIONAL

    await engine.dispose()
