"""API endpoints for Requirements"""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_suggestions.event_driven import generate_suggestions_for_requirement
from app.auth.dependencies import get_current_user, require_reviewer_or_admin
from app.config import settings
from app.crud import audit_log as crud_audit
from app.crud import requirement as crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit_log import AuditLogCreate
from app.schemas.requirement import (
    RequirementCreate,
    RequirementResponse,
    RequirementUpdate,
)

router = APIRouter()


@router.post("/requirements", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
async def create_requirement(
    requirement: RequirementCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_reviewer_or_admin),
):
    """Create a new requirement"""
    # Check if external_id already exists
    if requirement.external_id:
        existing = await crud.get_requirement_by_external_id(db, requirement.external_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requirement with external_id '{requirement.external_id}' already exists",
            )

    new_requirement = await crud.create_requirement(db, requirement)

    await crud_audit.create_audit_log(
        db,
        AuditLogCreate(
            user_id=current_user.id, action="create", resource_type="requirement", resource_id=str(new_requirement.id)
        ),
    )

    # Trigger auto-suggestion generation in background if enabled
    if settings.AUTO_SUGGESTIONS_ENABLED:
        background_tasks.add_task(
            generate_suggestions_for_requirement,
            new_requirement.id,
            db,
        )

    return new_requirement


@router.get("/requirements", response_model=list[RequirementResponse])
async def list_requirements(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all requirements"""
    return await crud.get_requirements(db, skip=skip, limit=limit)


@router.get("/requirements/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(
    requirement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific requirement by ID"""
    requirement = await crud.get_requirement(db, requirement_id)
    if not requirement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requirement {requirement_id} not found")
    return requirement


@router.put("/requirements/{requirement_id}", response_model=RequirementResponse)
async def update_requirement(
    requirement_id: UUID,
    requirement: RequirementUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_reviewer_or_admin),
):
    """Update a requirement"""
    updated = await crud.update_requirement(db, requirement_id, requirement)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requirement {requirement_id} not found")

    await crud_audit.create_audit_log(
        db,
        AuditLogCreate(
            user_id=current_user.id, action="update", resource_type="requirement", resource_id=str(requirement_id)
        ),
    )

    # Trigger auto-suggestion generation in background if enabled
    if settings.AUTO_SUGGESTIONS_ENABLED:
        background_tasks.add_task(
            generate_suggestions_for_requirement,
            requirement_id,
            db,
        )

    return updated


@router.delete("/requirements/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_requirement(
    requirement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_reviewer_or_admin),
):
    """Delete a requirement"""
    deleted = await crud.delete_requirement(db, requirement_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requirement {requirement_id} not found")

    await crud_audit.create_audit_log(
        db,
        AuditLogCreate(
            user_id=current_user.id, action="delete", resource_type="requirement", resource_id=str(requirement_id)
        ),
    )

