"""CRUD operations for Links and Suggestions"""

from datetime import datetime
from typing import List, Optional, NamedTuple
from uuid import UUID

from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.link import RequirementTestCaseLink
from app.models.suggestion import LinkSuggestion, SuggestionStatus
from app.models.requirement import Requirement
from app.models.test_case import TestCase
from app.schemas.link import LinkCreate, SuggestionCreate, SuggestionReview


class BatchReviewResult(NamedTuple):
    """Result of batch review operation"""
    total: int
    accepted: int
    rejected: int
    errors: List[str]


# Link operations
async def get_link(db: AsyncSession, link_id: UUID) -> Optional[RequirementTestCaseLink]:
    """Get a link by ID"""
    result = await db.execute(select(RequirementTestCaseLink).where(RequirementTestCaseLink.id == link_id))
    return result.scalar_one_or_none()


async def get_links(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[RequirementTestCaseLink]:
    """Get all links with pagination"""
    result = await db.execute(select(RequirementTestCaseLink).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_links_by_requirement(db: AsyncSession, requirement_id: UUID) -> List[RequirementTestCaseLink]:
    """Get all links for a requirement"""
    result = await db.execute(
        select(RequirementTestCaseLink).where(RequirementTestCaseLink.requirement_id == requirement_id)
    )
    return list(result.scalars().all())


async def get_links_by_test_case(db: AsyncSession, test_case_id: UUID) -> List[RequirementTestCaseLink]:
    """Get all links for a test case"""
    result = await db.execute(
        select(RequirementTestCaseLink).where(RequirementTestCaseLink.test_case_id == test_case_id)
    )
    return list(result.scalars().all())


async def create_link(db: AsyncSession, link: LinkCreate) -> RequirementTestCaseLink:
    """Create a new link"""
    db_link = RequirementTestCaseLink(**link.model_dump())
    db.add(db_link)
    await db.commit()
    await db.refresh(db_link)
    return db_link


async def delete_link(db: AsyncSession, link_id: UUID) -> bool:
    """Delete a link"""
    db_link = await get_link(db, link_id)
    if not db_link:
        return False

    await db.delete(db_link)
    await db.commit()
    return True


# Suggestion operations
async def get_suggestion(db: AsyncSession, suggestion_id: UUID) -> Optional[LinkSuggestion]:
    """Get a suggestion by ID"""
    result = await db.execute(select(LinkSuggestion).where(LinkSuggestion.id == suggestion_id))
    return result.scalar_one_or_none()


async def get_suggestions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[LinkSuggestion]:
    """Get all suggestions with pagination"""
    result = await db.execute(select(LinkSuggestion).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_pending_suggestions(
    db: AsyncSession,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    algorithm: Optional[str] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    search: Optional[str] = None,
    sort_by: str = "similarity_score",
    sort_order: str = "desc",
    limit: int = 100,
    offset: int = 0,
) -> List[LinkSuggestion]:
    """Get pending suggestions with filtering and sorting"""
    
    query = select(LinkSuggestion).where(LinkSuggestion.status == SuggestionStatus.PENDING)
    
    # Apply filters
    if min_score is not None:
        query = query.where(LinkSuggestion.similarity_score >= min_score)
    if max_score is not None:
        query = query.where(LinkSuggestion.similarity_score <= max_score)
    if algorithm:
        query = query.where(LinkSuggestion.suggestion_method == algorithm)
    if created_after:
        query = query.where(LinkSuggestion.created_at >= created_after)
    if created_before:
        query = query.where(LinkSuggestion.created_at <= created_before)
    
    # Search in requirement/test case titles if provided
    if search:
        # Join with requirements and test cases for search
        query = (
            query.join(Requirement, LinkSuggestion.requirement_id == Requirement.id)
            .join(TestCase, LinkSuggestion.test_case_id == TestCase.id)
            .where(
                or_(
                    Requirement.title.ilike(f"%{search}%"),
                    TestCase.title.ilike(f"%{search}%"),
                )
            )
        )
    
    # Apply sorting
    if sort_by == "similarity_score":
        order_col = LinkSuggestion.similarity_score
    elif sort_by == "created_at":
        order_col = LinkSuggestion.created_at
    else:
        order_col = LinkSuggestion.similarity_score
    
    if sort_order == "asc":
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def batch_review_suggestions(
    db: AsyncSession, suggestion_ids: List[UUID], review: SuggestionReview
) -> BatchReviewResult:
    """
    Batch review multiple suggestions
    Returns: BatchReviewResult with total, accepted, rejected counts and errors
    """
    errors = []
    accepted = 0
    rejected = 0
    
    for suggestion_id in suggestion_ids:
        try:
            result = await review_suggestion(db, suggestion_id, review)
            if result:
                if review.status == SuggestionStatus.ACCEPTED:
                    accepted += 1
                elif review.status == SuggestionStatus.REJECTED:
                    rejected += 1
            else:
                errors.append(f"Suggestion {suggestion_id} not found")
        except Exception as e:
            errors.append(f"Error reviewing {suggestion_id}: {str(e)}")
    
    return BatchReviewResult(
        total=len(suggestion_ids),
        accepted=accepted,
        rejected=rejected,
        errors=errors
    )


async def create_suggestion(db: AsyncSession, suggestion: SuggestionCreate) -> LinkSuggestion:
    """Create a new suggestion"""
    db_suggestion = LinkSuggestion(**suggestion.model_dump())
    db.add(db_suggestion)
    await db.commit()
    await db.refresh(db_suggestion)
    return db_suggestion


async def review_suggestion(
    db: AsyncSession, suggestion_id: UUID, review: SuggestionReview
) -> Optional[LinkSuggestion]:
    """Review a suggestion (accept/reject)"""
    db_suggestion = await get_suggestion(db, suggestion_id)
    if not db_suggestion:
        return None

    db_suggestion.status = review.status
    db_suggestion.feedback = review.feedback
    db_suggestion.reviewed_by = review.reviewed_by
    db_suggestion.reviewed_at = datetime.utcnow()

    await db.commit()
    await db.refresh(db_suggestion)
    return db_suggestion
