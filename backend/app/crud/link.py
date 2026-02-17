"""CRUD operations for Links and Suggestions"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.link import RequirementTestCaseLink
from app.models.suggestion import LinkSuggestion
from app.schemas.link import LinkCreate, SuggestionCreate, SuggestionReview


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
    sort_by: str = "score",
    sort_order: str = "desc",
    limit: int = 100,
) -> List[LinkSuggestion]:
    """Get pending suggestions with filters and sorting"""
    from app.models.suggestion import SuggestionMethod, SuggestionStatus

    query = select(LinkSuggestion).where(LinkSuggestion.status == SuggestionStatus.PENDING)

    # Apply filters
    if min_score is not None:
        query = query.where(LinkSuggestion.similarity_score >= min_score)
    if max_score is not None:
        query = query.where(LinkSuggestion.similarity_score <= max_score)
    if algorithm:
        # Map algorithm name to enum value
        # Note: 'tfidf' maps to SEMANTIC_SIMILARITY as TF-IDF is the core semantic similarity algorithm
        method_map = {
            "tfidf": SuggestionMethod.SEMANTIC_SIMILARITY,
            "keyword": SuggestionMethod.KEYWORD_MATCH,
            "hybrid": SuggestionMethod.HYBRID,
            "llm": SuggestionMethod.LLM_EMBEDDING,
        }
        if algorithm in method_map:
            query = query.where(LinkSuggestion.suggestion_method == method_map[algorithm])

    # Apply sorting
    if sort_by == "score":
        order_col = LinkSuggestion.similarity_score
    elif sort_by == "date":
        order_col = LinkSuggestion.created_at
    elif sort_by == "algorithm":
        order_col = LinkSuggestion.suggestion_method
    else:
        order_col = LinkSuggestion.similarity_score

    if sort_order == "asc":
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())

    query = query.limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


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


async def bulk_review_suggestions(
    db: AsyncSession,
    suggestion_ids: List[UUID],
    status,
    feedback: Optional[str] = None,
    reviewed_by: Optional[str] = None,
) -> int:
    """Review multiple suggestions at once"""
    from app.models.suggestion import SuggestionStatus

    stmt = (
        update(LinkSuggestion)
        .where(LinkSuggestion.id.in_(suggestion_ids))
        .where(LinkSuggestion.status == SuggestionStatus.PENDING)
        .values(status=status, feedback=feedback, reviewed_by=reviewed_by, reviewed_at=datetime.utcnow())
    )

    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount
