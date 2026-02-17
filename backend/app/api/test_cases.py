"""API endpoints for Test Cases"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_suggestions.event_driven import generate_suggestions_for_test_case
from app.config import settings
from app.crud import test_case as crud
from app.db.session import get_db
from app.schemas.test_case import TestCaseCreate, TestCaseResponse, TestCaseUpdate

router = APIRouter()


@router.post("/test-cases", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case: TestCaseCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Create a new test case"""
    # Check if external_id already exists
    if test_case.external_id:
        existing = await crud.get_test_case_by_external_id(db, test_case.external_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Test case with external_id '{test_case.external_id}' already exists",
            )

    new_test_case = await crud.create_test_case(db, test_case)

    # Trigger auto-suggestion generation in background if enabled
    if settings.AUTO_SUGGESTIONS_ENABLED:
        background_tasks.add_task(
            generate_suggestions_for_test_case,
            new_test_case.id,
            db,
        )

    return new_test_case


@router.get("/test-cases", response_model=List[TestCaseResponse])
async def list_test_cases(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all test cases"""
    return await crud.get_test_cases(db, skip=skip, limit=limit)


@router.get("/test-cases/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(test_case_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific test case by ID"""
    test_case = await crud.get_test_case(db, test_case_id)
    if not test_case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Test case {test_case_id} not found")
    return test_case


@router.put("/test-cases/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    test_case_id: UUID,
    test_case: TestCaseUpdate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Update a test case"""
    updated = await crud.update_test_case(db, test_case_id, test_case)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Test case {test_case_id} not found")

    # Trigger auto-suggestion generation in background if enabled
    if settings.AUTO_SUGGESTIONS_ENABLED:
        background_tasks.add_task(
            generate_suggestions_for_test_case,
            test_case_id,
            db,
        )

    return updated


@router.delete("/test-cases/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(test_case_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a test case"""
    deleted = await crud.delete_test_case(db, test_case_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Test case {test_case_id} not found")
