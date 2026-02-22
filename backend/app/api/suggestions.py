"""API endpoints for AI Suggestion Generation"""

import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai_suggestions.config import SuggestionConfig
from app.ai_suggestions.engine import SuggestionEngine
from app.auth.dependencies import get_current_user, require_admin
from app.crud.audit_log import create_audit_entry
from app.db.session import get_db
from app.models.suggestion import LinkSuggestion, SuggestionStatus
from app.models.user import User

router = APIRouter()


@router.get("/suggestions/export/csv")
async def export_suggestions_csv(
    status: str | None = Query(None, description="Filter by status: pending, accepted, rejected"),
    algorithm: str | None = Query(None, description="Filter by algorithm"),
    min_score: float | None = Query(None, ge=0.0, le=1.0, description="Minimum confidence score"),
    max_score: float | None = Query(None, ge=0.0, le=1.0, description="Maximum confidence score"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export suggestions as CSV with optional filtering.

    Supports filtering by status, algorithm, and confidence score range.
    """
    query = select(LinkSuggestion).options(
        selectinload(LinkSuggestion.requirement),
        selectinload(LinkSuggestion.test_case),
    )

    if status is not None:
        try:
            status_enum = SuggestionStatus(status.lower())
            query = query.where(LinkSuggestion.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status '{status}'. Must be one of: pending, accepted, rejected.",
            )

    if algorithm is not None:
        from app.models.suggestion import SuggestionMethod

        try:
            method_enum = SuggestionMethod(algorithm.lower())
            query = query.where(LinkSuggestion.suggestion_method == method_enum)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid algorithm '{algorithm}'.",
            )

    if min_score is not None:
        query = query.where(LinkSuggestion.similarity_score >= min_score)

    if max_score is not None:
        query = query.where(LinkSuggestion.similarity_score <= max_score)

    result = await db.execute(query)
    suggestions = result.scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "ID",
            "Requirement Title",
            "Test Case Title",
            "Algorithm",
            "Confidence Score",
            "Status",
            "Reviewed By",
            "Feedback",
            "Created At",
            "Reviewed At",
        ]
    )
    for s in suggestions:
        writer.writerow(
            [
                str(s.id),
                s.requirement.title if s.requirement else "",
                s.test_case.title if s.test_case else "",
                s.suggestion_method.value if s.suggestion_method else "",
                f"{s.similarity_score:.4f}" if s.similarity_score is not None else "",
                s.status.value if s.status else "",
                s.reviewed_by or "",
                s.feedback or "",
                s.created_at.isoformat() if s.created_at else "",
                s.reviewed_at.isoformat() if s.reviewed_at else "",
            ]
        )

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=suggestions.csv"},
    )


@router.post("/suggestions/generate", response_model=dict)
async def generate_suggestions(
    algorithm: str | None = Query(
        None, description="Algorithm to use: 'tfidf', 'keyword', 'hybrid', or 'llm'. Uses default if not specified."
    ),
    threshold: float | None = Query(
        None, ge=0.0, le=1.0, description="Minimum confidence threshold (0.0-1.0). Uses default if not specified."
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Generate AI-powered link suggestions for all requirements and test cases.

    This endpoint analyzes all requirements and test cases in the database,
    computes similarity scores using the specified algorithm, and creates
    LinkSuggestion records for pairs that exceed the confidence threshold.

    The engine is idempotent - running it multiple times will not create
    duplicate suggestions for the same requirement-test case pairs.

    Returns:
        Dictionary with generation statistics:
        - pairs_analyzed: Total number of requirement-test case pairs analyzed
        - suggestions_created: Number of new suggestions created
        - suggestions_skipped: Number of pairs skipped (existing link/suggestion or below threshold)
        - algorithm_used: The similarity algorithm used
        - threshold: The confidence threshold applied
    """
    try:
        # Create config with optional overrides
        config = SuggestionConfig()
        if algorithm:
            if algorithm.lower() not in ["tfidf", "keyword", "hybrid", "llm"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid algorithm: {algorithm}. Must be 'tfidf', 'keyword', 'hybrid', or 'llm'.",
                )
            config.default_algorithm = algorithm.lower()

        if threshold is not None:
            config.min_confidence_threshold = threshold

        # Initialize engine and generate suggestions
        engine = SuggestionEngine(config=config)
        result = await engine.generate_suggestions(db)

        await create_audit_entry(
            db,
            user_id=current_user.id,
            action="suggestion.generated",
            resource_type="suggestion",
            resource_id="bulk",
            details=result,
        )

        return {"message": "Suggestion generation completed", "results": result}

    except ImportError as e:
        if "scikit-learn" in str(e):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="TF-IDF algorithm requires scikit-learn. Please install it or use 'keyword' algorithm.",
            )
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating suggestions: {str(e)}"
        )
