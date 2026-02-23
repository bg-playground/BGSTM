"""API endpoints for Test Cases"""

import math
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_suggestions.event_driven import generate_suggestions_for_test_case
from app.auth.dependencies import get_current_user, require_reviewer_or_admin
from app.config import settings
from app.crud import test_case as crud
from app.crud.audit_log import create_audit_entry
from app.db.session import get_db
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.schemas.test_case import TestCaseCreate, TestCaseResponse, TestCaseUpdate

router = APIRouter()


@router.post("/test-cases", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case: TestCaseCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_reviewer_or_admin),
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

    await create_audit_entry(
        db,
        user_id=current_user.id,
        action="test_case.created",
        resource_type="test_case",
        resource_id=str(new_test_case.id),
        details={"title": new_test_case.title},
    )

    try:
        from app.services.notification_service import notify_test_case_created

        await notify_test_case_created(
            db,
            creator_user_id=current_user.id,
            test_case_title=new_test_case.title,
            metadata={"test_case_id": str(new_test_case.id)},
        )
    except Exception:
        pass

    # Trigger auto-suggestion generation in background if enabled
    if settings.AUTO_SUGGESTIONS_ENABLED:
        background_tasks.add_task(
            generate_suggestions_for_test_case,
            new_test_case.id,
            db,
        )

    return new_test_case


@router.get("/test-cases", response_model=PaginatedResponse[TestCaseResponse])
async def list_test_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all test cases"""
    skip = (page - 1) * page_size
    items, total = await crud.get_test_cases(db, skip=skip, limit=page_size)
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/test-cases/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(
    test_case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
    current_user: User = Depends(require_reviewer_or_admin),
):
    """Update a test case"""
    updated = await crud.update_test_case(db, test_case_id, test_case)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Test case {test_case_id} not found")

    await create_audit_entry(
        db,
        user_id=current_user.id,
        action="test_case.updated",
        resource_type="test_case",
        resource_id=str(test_case_id),
        details={"title": updated.title},
    )

    # Trigger auto-suggestion generation in background if enabled
    if settings.AUTO_SUGGESTIONS_ENABLED:
        background_tasks.add_task(
            generate_suggestions_for_test_case,
            test_case_id,
            db,
        )

    return updated


@router.delete("/test-cases/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(
    test_case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_reviewer_or_admin),
):
    """Delete a test case"""
    deleted = await crud.delete_test_case(db, test_case_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Test case {test_case_id} not found")

    await create_audit_entry(
        db,
        user_id=current_user.id,
        action="test_case.deleted",
        resource_type="test_case",
        resource_id=str(test_case_id),
    )
