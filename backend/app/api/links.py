"""API endpoints for Links and Suggestions"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.link import LinkCreate, LinkResponse, SuggestionResponse, SuggestionReview
from app.crud import link as crud

router = APIRouter()


# Link endpoints
@router.post("/links", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    link: LinkCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new requirement-test case link"""
    try:
        return await crud.create_link(db, link)
    except Exception as e:
        # Handle unique constraint violation
        if "uq_requirement_test_case" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Link between this requirement and test case already exists"
            )
        raise


@router.get("/links", response_model=List[LinkResponse])
async def list_links(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all links"""
    return await crud.get_links(db, skip=skip, limit=limit)


@router.get("/links/{link_id}", response_model=LinkResponse)
async def get_link(
    link_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific link by ID"""
    link = await crud.get_link(db, link_id)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link {link_id} not found"
        )
    return link


@router.get("/requirements/{requirement_id}/links", response_model=List[LinkResponse])
async def get_requirement_links(
    requirement_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all links for a specific requirement"""
    return await crud.get_links_by_requirement(db, requirement_id)


@router.get("/test-cases/{test_case_id}/links", response_model=List[LinkResponse])
async def get_test_case_links(
    test_case_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get all links for a specific test case"""
    return await crud.get_links_by_test_case(db, test_case_id)


@router.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    link_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a link"""
    deleted = await crud.delete_link(db, link_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link {link_id} not found"
        )


# Suggestion endpoints
@router.get("/suggestions", response_model=List[SuggestionResponse])
async def list_suggestions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all link suggestions"""
    return await crud.get_suggestions(db, skip=skip, limit=limit)


@router.get("/suggestions/pending", response_model=List[SuggestionResponse])
async def list_pending_suggestions(
    db: AsyncSession = Depends(get_db)
):
    """List all pending link suggestions"""
    return await crud.get_pending_suggestions(db)


@router.get("/suggestions/{suggestion_id}", response_model=SuggestionResponse)
async def get_suggestion(
    suggestion_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific suggestion by ID"""
    suggestion = await crud.get_suggestion(db, suggestion_id)
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suggestion {suggestion_id} not found"
        )
    return suggestion


@router.post("/suggestions/{suggestion_id}/review", response_model=SuggestionResponse)
async def review_suggestion(
    suggestion_id: UUID,
    review: SuggestionReview,
    db: AsyncSession = Depends(get_db)
):
    """Review a suggestion (accept/reject)"""
    reviewed = await crud.review_suggestion(db, suggestion_id, review)
    if not reviewed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suggestion {suggestion_id} not found"
        )
    return reviewed
