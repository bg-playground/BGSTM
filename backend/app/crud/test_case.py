"""CRUD operations for Test Cases"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_case import TestCase
from app.schemas.test_case import TestCaseCreate, TestCaseUpdate


async def get_test_case(db: AsyncSession, test_case_id: UUID) -> TestCase | None:
    """Get a test case by ID"""
    result = await db.execute(select(TestCase).where(TestCase.id == test_case_id))
    return result.scalar_one_or_none()


async def get_test_case_by_external_id(db: AsyncSession, external_id: str) -> TestCase | None:
    """Get a test case by external ID"""
    result = await db.execute(select(TestCase).where(TestCase.external_id == external_id))
    return result.scalar_one_or_none()


async def get_test_cases(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[TestCase]:
    """Get all test cases with pagination"""
    result = await db.execute(select(TestCase).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_test_case(db: AsyncSession, test_case: TestCaseCreate) -> TestCase:
    """Create a new test case"""
    db_test_case = TestCase(**test_case.model_dump())
    db.add(db_test_case)
    await db.commit()
    await db.refresh(db_test_case)
    return db_test_case


async def update_test_case(db: AsyncSession, test_case_id: UUID, test_case: TestCaseUpdate) -> TestCase | None:
    """Update a test case"""
    db_test_case = await get_test_case(db, test_case_id)
    if not db_test_case:
        return None

    update_data = test_case.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_test_case, field, value)

    await db.commit()
    await db.refresh(db_test_case)
    return db_test_case


async def delete_test_case(db: AsyncSession, test_case_id: UUID) -> bool:
    """Delete a test case"""
    db_test_case = await get_test_case(db, test_case_id)
    if not db_test_case:
        return False

    await db.delete(db_test_case)
    await db.commit()
    return True
