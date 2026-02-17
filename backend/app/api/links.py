"""API endpoints for Links and Suggestions"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import link as crud
from app.db.session import get_db
from app.schemas.link import (
    BatchReviewResult,
    BatchSuggestionReview,
    LinkCreate,
    LinkResponse,
    SuggestionResponse,
    SuggestionReview,
)

router = APIRouter()


# Link endpoints
@router.post("/links", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(link: LinkCreate, db: AsyncSession = Depends(get_db)):
    """Create a new requirement-test case link"""
    try:
        return await crud.create_link(db, link)
    except Exception as e:
        # Handle unique constraint violation
        if "uq_requirement_test_case" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Link between this requirement and test case already exists",
            )
        raise


@router.get("/links", response_model=List[LinkResponse])
async def list_links(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all links"""
    return await crud.get_links(db, skip=skip, limit=limit)


@router.get("/links/{link_id}", response_model=LinkResponse)
async def get_link(link_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific link by ID"""
    link = await crud.get_link(db, link_id)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Link {link_id} not found")
    return link


@router.get("/requirements/{requirement_id}/links", response_model=List[LinkResponse])
async def get_requirement_links(requirement_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get all links for a specific requirement"""
    return await crud.get_links_by_requirement(db, requirement_id)


@router.get("/test-cases/{test_case_id}/links", response_model=List[LinkResponse])
async def get_test_case_links(test_case_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get all links for a specific test case"""
    return await crud.get_links_by_test_case(db, test_case_id)


@router.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(link_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a link"""
    deleted = await crud.delete_link(db, link_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Link {link_id} not found")


# Suggestion endpoints
@router.get("/suggestions", response_model=List[SuggestionResponse])
async def list_suggestions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all link suggestions"""
    return await crud.get_suggestions(db, skip=skip, limit=limit)


@router.get("/suggestions/pending", response_model=List[SuggestionResponse])
async def list_pending_suggestions(
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence score"),
    max_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Maximum confidence score"),
    algorithm: Optional[str] = Query(None, description="Filter by algorithm"),
    created_after: Optional[datetime] = Query(None, description="Filter by creation date (after)"),
    created_before: Optional[datetime] = Query(None, description="Filter by creation date (before)"),
    search: Optional[str] = Query(None, description="Search in requirement/test case titles"),
    sort_by: Optional[str] = Query("similarity_score", regex="^(similarity_score|created_at)$"),
    sort_order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    limit: Optional[int] = Query(100, le=500, description="Maximum number of results"),
    offset: Optional[int] = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
):
    """List pending suggestions with advanced filtering and sorting"""
    return await crud.get_pending_suggestions(
        db=db,
        min_score=min_score,
        max_score=max_score,
        algorithm=algorithm,
        created_after=created_after,
        created_before=created_before,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset,
    )


@router.get("/suggestions/{suggestion_id}", response_model=SuggestionResponse)
async def get_suggestion(suggestion_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific suggestion by ID"""
    suggestion = await crud.get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Suggestion {suggestion_id} not found")
    return suggestion


@router.post("/suggestions/{suggestion_id}/review", response_model=SuggestionResponse)
async def review_suggestion(suggestion_id: UUID, review: SuggestionReview, db: AsyncSession = Depends(get_db)):
    """Review a suggestion (accept/reject)"""
    reviewed = await crud.review_suggestion(db, suggestion_id, review)
    if not reviewed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Suggestion {suggestion_id} not found")
    return reviewed


@router.post("/suggestions/batch-review", response_model=BatchReviewResult)
async def batch_review_suggestions(
    batch_review: BatchSuggestionReview,
    db: AsyncSession = Depends(get_db),
):
    """
    Review multiple suggestions at once
    
    Request body:
    {
        "suggestion_ids": ["uuid1", "uuid2", ...],
        "status": "accepted" | "rejected",
        "reviewed_by": "user@example.com",
        "feedback": "Optional batch feedback"
    }
    
    Returns:
    {
        "total": 10,
        "accepted": 10,
        "rejected": 0,
        "failed": 0,
        "errors": []
    }
    """
    review = SuggestionReview(
        status=batch_review.status,
        reviewed_by=batch_review.reviewed_by,
        feedback=batch_review.feedback,
    )
    
    total, accepted, rejected, errors = await crud.batch_review_suggestions(
        db, batch_review.suggestion_ids, review
    )
    
    return BatchReviewResult(
        total=total,
        accepted=accepted,
        rejected=rejected,
        failed=len(errors),
        errors=errors,
    )
