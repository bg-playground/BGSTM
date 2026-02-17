"""API endpoints for AI Suggestion Generation"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_suggestions.config import SuggestionConfig
from app.ai_suggestions.engine import SuggestionEngine
from app.db.session import get_db

router = APIRouter()


@router.post("/suggestions/generate", response_model=Dict[str, Any])
async def generate_suggestions(
    algorithm: Optional[str] = Query(
        None, description="Algorithm to use: 'tfidf', 'keyword', 'hybrid', or 'llm'. Uses default if not specified."
    ),
    threshold: Optional[float] = Query(
        None, ge=0.0, le=1.0, description="Minimum confidence threshold (0.0-1.0). Uses default if not specified."
    ),
    db: AsyncSession = Depends(get_db),
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
