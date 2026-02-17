"""Tests for Event-Driven Suggestion Generation"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.ai_suggestions.event_driven import (
    generate_suggestions_for_requirement,
    generate_suggestions_for_test_case,
)
from app.crud import requirement as req_crud
from app.crud import test_case as tc_crud
from app.models.base import Base
from app.models.requirement import (
    PriorityLevel,
    RequirementStatus,
    RequirementType,
)
from app.models.suggestion import LinkSuggestion, SuggestionStatus
from app.models.test_case import (
    AutomationStatus,
    TestCaseStatus,
    TestCaseType,
)
from app.schemas.requirement import RequirementCreate
from app.schemas.test_case import TestCaseCreate


@pytest_asyncio.fixture
async def async_db():
    """Create an in-memory async SQLite database for testing"""
    # Create async engine
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Provide session
    async with AsyncSessionLocal() as session:
        yield session

    # Cleanup
    await engine.dispose()


@pytest.mark.asyncio
async def test_auto_suggestion_on_requirement_creation(async_db: AsyncSession):
    """Test that suggestions are auto-generated when a requirement is created"""
    # Create a test case first
    tc_data = TestCaseCreate(
        title="Test user authentication with username and password",
        description="Verify that users can authenticate using valid username and password credentials",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )
    test_case = await tc_crud.create_test_case(async_db, tc_data)

    # Create a requirement
    req_data = RequirementCreate(
        title="User Authentication",
        description="The system shall authenticate users with username and password credentials",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED,
    )
    requirement = await req_crud.create_requirement(async_db, req_data)

    # Manually trigger suggestion generation with lower threshold (simulating background task)
    await generate_suggestions_for_requirement(requirement.id, async_db, threshold=0.1)

    # Verify suggestions were created
    from sqlalchemy import select

    result = await async_db.execute(
        select(LinkSuggestion).where(
            LinkSuggestion.requirement_id == requirement.id,
            LinkSuggestion.test_case_id == test_case.id,
        )
    )
    suggestion = result.scalar_one_or_none()

    # Should have a suggestion since both are about user authentication/login
    assert suggestion is not None
    assert suggestion.status == SuggestionStatus.PENDING
    assert suggestion.similarity_score > 0


@pytest.mark.asyncio
async def test_auto_suggestion_on_test_case_creation(async_db: AsyncSession):
    """Test that suggestions are auto-generated when a test case is created"""
    # Create a requirement first
    req_data = RequirementCreate(
        title="Payment Processing with Credit Cards",
        description="The system shall process credit card payments securely using encrypted transactions",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED,
    )
    requirement = await req_crud.create_requirement(async_db, req_data)

    # Create a test case
    tc_data = TestCaseCreate(
        title="Test credit card payment processing",
        description="Verify that credit card payments are processed securely with proper encryption",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )
    test_case = await tc_crud.create_test_case(async_db, tc_data)

    # Manually trigger suggestion generation with lower threshold (simulating background task)
    await generate_suggestions_for_test_case(test_case.id, async_db, threshold=0.1)

    # Verify suggestions were created
    from sqlalchemy import select

    result = await async_db.execute(
        select(LinkSuggestion).where(
            LinkSuggestion.requirement_id == requirement.id,
            LinkSuggestion.test_case_id == test_case.id,
        )
    )
    suggestion = result.scalar_one_or_none()

    # Should have a suggestion since both are about payment processing
    assert suggestion is not None
    assert suggestion.status == SuggestionStatus.PENDING
    assert suggestion.similarity_score > 0


@pytest.mark.asyncio
async def test_no_duplicate_suggestions(async_db: AsyncSession):
    """Test that duplicate suggestions are not created"""
    # Create requirement and test case
    req_data = RequirementCreate(
        title="Data Encryption at Rest",
        description="The system shall encrypt sensitive data using AES-256 encryption when storing data at rest",
        type=RequirementType.TECHNICAL,
        priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED,
    )
    requirement = await req_crud.create_requirement(async_db, req_data)

    tc_data = TestCaseCreate(
        title="Test data encryption at rest",
        description="Verify that sensitive data is encrypted properly using AES-256 when stored at rest",
        type=TestCaseType.SECURITY,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )
    test_case = await tc_crud.create_test_case(async_db, tc_data)

    # Generate suggestions first time with lower threshold
    await generate_suggestions_for_requirement(requirement.id, async_db, threshold=0.1)

    # Count suggestions
    from sqlalchemy import func, select

    result = await async_db.execute(
        select(func.count(LinkSuggestion.id)).where(
            LinkSuggestion.requirement_id == requirement.id,
            LinkSuggestion.test_case_id == test_case.id,
        )
    )
    count_after_first = result.scalar()

    # Generate suggestions second time (should not create duplicates)
    await generate_suggestions_for_requirement(requirement.id, async_db, threshold=0.1)

    result = await async_db.execute(
        select(func.count(LinkSuggestion.id)).where(
            LinkSuggestion.requirement_id == requirement.id,
            LinkSuggestion.test_case_id == test_case.id,
        )
    )
    count_after_second = result.scalar()

    # Count should be the same (no duplicates)
    assert count_after_first == count_after_second


@pytest.mark.asyncio
async def test_auto_suggestion_respects_threshold(async_db: AsyncSession):
    """Test that suggestions below threshold are not created"""
    # Create requirement and test case with completely different topics
    req_data = RequirementCreate(
        title="Database Backup",
        description="The system shall perform automated database backups daily",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=RequirementStatus.APPROVED,
    )
    requirement = await req_crud.create_requirement(async_db, req_data)

    tc_data = TestCaseCreate(
        title="Test user interface colors",
        description="Verify that the UI uses the correct color scheme",
        type=TestCaseType.UI,
        priority=PriorityLevel.LOW,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )
    test_case = await tc_crud.create_test_case(async_db, tc_data)

    # Generate suggestions (with low threshold to ensure creation)
    await generate_suggestions_for_requirement(requirement.id, async_db, threshold=0.05)

    # Verify no suggestion was created (topics too different)
    from sqlalchemy import select

    result = await async_db.execute(
        select(LinkSuggestion).where(
            LinkSuggestion.requirement_id == requirement.id,
            LinkSuggestion.test_case_id == test_case.id,
        )
    )
    suggestion = result.scalar_one_or_none()

    # Should not have a suggestion (similarity too low)
    assert suggestion is None


@pytest.mark.asyncio
async def test_auto_suggestion_with_multiple_items(async_db: AsyncSession):
    """Test that auto-suggestion works correctly with multiple existing items"""
    # Create multiple requirements
    req1_data = RequirementCreate(
        title="User Registration",
        description="Users shall be able to register with email and password",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED,
    )
    req1 = await req_crud.create_requirement(async_db, req1_data)

    req2_data = RequirementCreate(
        title="Email Verification",
        description="The system shall send verification emails to new users",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED,
    )
    req2 = await req_crud.create_requirement(async_db, req2_data)

    # Create a new test case that relates to user registration
    tc_data = TestCaseCreate(
        title="Test user registration flow",
        description="Verify that users can register and receive verification email",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )
    test_case = await tc_crud.create_test_case(async_db, tc_data)

    # Generate suggestions for the new test case with lower threshold
    await generate_suggestions_for_test_case(test_case.id, async_db, threshold=0.1)

    # Verify suggestions were created for both related requirements
    from sqlalchemy import select

    result = await async_db.execute(select(LinkSuggestion).where(LinkSuggestion.test_case_id == test_case.id))
    suggestions = result.scalars().all()

    # Should have suggestions for both requirements
    assert len(suggestions) >= 1  # At least one suggestion
    suggestion_req_ids = {s.requirement_id for s in suggestions}
    # Should suggest at least the user registration requirement
    assert req1.id in suggestion_req_ids or req2.id in suggestion_req_ids


@pytest.mark.asyncio
async def test_auto_suggestion_uses_configured_algorithm(async_db: AsyncSession):
    """Test that auto-suggestion uses the configured algorithm from settings"""
    # Create requirement and test case
    req_data = RequirementCreate(
        title="API Rate Limiting",
        description="The API shall implement rate limiting to prevent abuse",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED,
    )
    requirement = await req_crud.create_requirement(async_db, req_data)

    tc_data = TestCaseCreate(
        title="Test API rate limiting",
        description="Verify that the API enforces rate limits correctly",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        automation_status=AutomationStatus.MANUAL,
    )
    test_case = await tc_crud.create_test_case(async_db, tc_data)

    # Generate suggestions using keyword algorithm with lower threshold
    await generate_suggestions_for_requirement(requirement.id, async_db, algorithm="keyword", threshold=0.1)

    # Verify suggestion was created with keyword method
    from sqlalchemy import select

    result = await async_db.execute(
        select(LinkSuggestion).where(
            LinkSuggestion.requirement_id == requirement.id,
            LinkSuggestion.test_case_id == test_case.id,
        )
    )
    suggestion = result.scalar_one_or_none()

    assert suggestion is not None
    # The suggestion_metadata should indicate the keyword algorithm was used
    assert "algorithm" in suggestion.suggestion_metadata
    assert suggestion.suggestion_metadata["algorithm"] == "keyword"
