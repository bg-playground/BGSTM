"""CRUD operations for Requirements"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.requirement import Requirement
from app.schemas.requirement import RequirementCreate, RequirementUpdate


async def get_requirement(db: AsyncSession, requirement_id: UUID) -> Requirement | None:
    """Get a requirement by ID"""
    result = await db.execute(select(Requirement).where(Requirement.id == requirement_id))
    return result.scalar_one_or_none()


async def get_requirement_by_external_id(db: AsyncSession, external_id: str) -> Requirement | None:
    """Get a requirement by external ID"""
    result = await db.execute(select(Requirement).where(Requirement.external_id == external_id))
    return result.scalar_one_or_none()


async def get_requirements(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Requirement]:
    """Get all requirements with pagination"""
    result = await db.execute(select(Requirement).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_requirement(db: AsyncSession, requirement: RequirementCreate) -> Requirement:
    """Create a new requirement"""
    db_requirement = Requirement(**requirement.model_dump())
    db.add(db_requirement)
    await db.commit()
    await db.refresh(db_requirement)
    return db_requirement


async def update_requirement(
    db: AsyncSession, requirement_id: UUID, requirement: RequirementUpdate
) -> Requirement | None:
    """Update a requirement"""
    db_requirement = await get_requirement(db, requirement_id)
    if not db_requirement:
        return None

    update_data = requirement.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_requirement, field, value)

    await db.commit()
    await db.refresh(db_requirement)
    return db_requirement


async def delete_requirement(db: AsyncSession, requirement_id: UUID) -> bool:
    """Delete a requirement"""
    db_requirement = await get_requirement(db, requirement_id)
    if not db_requirement:
        return False

    await db.delete(db_requirement)
    await db.commit()
    return True
