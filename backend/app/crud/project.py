"""CRUD operations for Projects."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


async def create_project(db: AsyncSession, payload: ProjectCreate) -> Project:
    project = Project(**payload.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get_project(db: AsyncSession, project_id: UUID) -> Project | None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


async def list_projects(db: AsyncSession, skip: int = 0, limit: int = 100) -> tuple[list[Project], int]:
    count_result = await db.execute(select(func.count()).select_from(Project))
    total = count_result.scalar_one()
    result = await db.execute(select(Project).offset(skip).limit(limit))
    return list(result.scalars().all()), total


async def update_project(db: AsyncSession, project_id: UUID, payload: ProjectUpdate) -> Project | None:
    project = await get_project(db, project_id)
    if project is None:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project
