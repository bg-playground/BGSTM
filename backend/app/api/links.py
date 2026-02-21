"""API endpoints for Links and Suggestions"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import link as crud
from app.db.session import get_db
from app.schemas.link import (
    BulkReviewRequest,
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


@router.get("/links", response_model=list[LinkResponse])
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


@router.get("/requirements/{requirement_id}/links", response_model=list[LinkResponse])
async def get_requirement_links(requirement_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get all links for a specific requirement"""
    return await crud.get_links_by_requirement(db, requirement_id)


@router.get("/test-cases/{test_case_id}/links", response_model=list[LinkResponse])
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
@router.get("/suggestions", response_model=list[SuggestionResponse])
async def list_suggestions(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all link suggestions"""
    return await crud.get_suggestions(db, skip=skip, limit=limit)


@router.get("/suggestions/pending", response_model=list[SuggestionResponse])
async def list_pending_suggestions(
    min_score: float | None = Query(None, ge=0.0, le=1.0, description="Minimum similarity score"),
    max_score: float | None = Query(None, ge=0.0, le=1.0, description="Maximum similarity score"),
    algorithm: str | None = Query(None, description="Filter by algorithm (tfidf, keyword, hybrid, llm)"),
    sort_by: str | None = Query("score", description="Sort field: 'score', 'date', 'algorithm'"),
    sort_order: str | None = Query("desc", description="Sort order: 'asc' or 'desc'"),
    limit: int | None = Query(100, le=500, description="Maximum results to return"),
    search: str | None = Query(None, description="Search term to filter by requirement/test case title or description"),
    db: AsyncSession = Depends(get_db),
):
    """List pending suggestions with filtering and sorting"""
    return await crud.get_pending_suggestions(
        db,
        min_score=min_score,
        max_score=max_score,
        algorithm=algorithm,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        search=search,
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


@router.post("/suggestions/bulk-review", response_model=dict[str, Any])
async def bulk_review_suggestions(request: BulkReviewRequest, db: AsyncSession = Depends(get_db)):
    """Review multiple suggestions at once"""
    reviewed = await crud.bulk_review_suggestions(
        db, request.suggestion_ids, request.status, request.feedback, request.reviewed_by
    )

    return {"message": f"Reviewed {reviewed} suggestions", "count": reviewed, "status": request.status}
