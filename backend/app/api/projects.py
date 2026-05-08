"""API endpoints for Projects."""

import math
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_reviewer_or_admin
from app.crud import project as crud
from app.crud.audit_log import write_audit
from app.db.session import get_db
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter()


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_reviewer_or_admin),
) -> ProjectResponse:
    project = await crud.create_project(db, payload)
    await write_audit(
        db,
        actor_kind="user",
        actor_id=current_user.id,
        action="project.create",
        resource_type="project",
        resource_id=project.id,
        details=payload.model_dump(),
    )
    return project


@router.get("/projects", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> PaginatedResponse[ProjectResponse]:
    skip = (page - 1) * page_size
    items, total = await crud.list_projects(db, skip=skip, limit=page_size)
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ProjectResponse:
    project = await crud.get_project(db, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found")
    return project


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_reviewer_or_admin),
) -> ProjectResponse:
    existing = await crud.get_project(db, project_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found")

    changed_fields = payload.model_dump(exclude_unset=True)
    original_values = {field: getattr(existing, field) for field in changed_fields}
    updated = await crud.update_project(db, project_id, payload)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Project {project_id} not found")

    diff: dict[str, dict[str, Any]] = {}
    for field, new_value in changed_fields.items():
        old_value = original_values[field]
        if old_value != new_value:
            diff[field] = {"from": old_value, "to": new_value}

    await write_audit(
        db,
        actor_kind="user",
        actor_id=current_user.id,
        action="project.update",
        resource_type="project",
        resource_id=updated.id,
        details=diff,
    )
    return updated
