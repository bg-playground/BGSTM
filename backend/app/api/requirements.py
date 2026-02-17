"""API endpoints for Requirements"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import requirement as crud
from app.db.session import get_db
from app.schemas.requirement import (
    RequirementCreate,
    RequirementResponse,
    RequirementUpdate,
)

router = APIRouter()


@router.post("/requirements", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
async def create_requirement(requirement: RequirementCreate, db: AsyncSession = Depends(get_db)):
    """Create a new requirement"""
    # Check if external_id already exists
    if requirement.external_id:
        existing = await crud.get_requirement_by_external_id(db, requirement.external_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requirement with external_id '{requirement.external_id}' already exists",
            )

    return await crud.create_requirement(db, requirement)


@router.get("/requirements", response_model=List[RequirementResponse])
async def list_requirements(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all requirements"""
    return await crud.get_requirements(db, skip=skip, limit=limit)


@router.get("/requirements/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(requirement_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific requirement by ID"""
    requirement = await crud.get_requirement(db, requirement_id)
    if not requirement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requirement {requirement_id} not found")
    return requirement


@router.put("/requirements/{requirement_id}", response_model=RequirementResponse)
async def update_requirement(requirement_id: UUID, requirement: RequirementUpdate, db: AsyncSession = Depends(get_db)):
    """Update a requirement"""
    updated = await crud.update_requirement(db, requirement_id, requirement)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requirement {requirement_id} not found")
    return updated


@router.delete("/requirements/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_requirement(requirement_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a requirement"""
    deleted = await crud.delete_requirement(db, requirement_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requirement {requirement_id} not found")
