"""Analytics API endpoints"""

from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.analytics import SuggestionAnalytics

router = APIRouter()


@router.get("/analytics/acceptance-rates", response_model=dict[str, Any])
async def get_acceptance_rates(
    days: Optional[int] = Query(None, ge=1, le=365, description="Filter to last N days"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get suggestion acceptance rates overall and by algorithm

    Returns metrics on accepted, rejected, and pending suggestions
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days) if days else None

    return await SuggestionAnalytics.get_acceptance_rates(db, start_date, end_date)


@router.get("/analytics/confidence-distribution", response_model=dict[str, Any])
async def get_confidence_distribution(
    algorithm: Optional[str] = Query(None, description="Filter by algorithm: tfidf, keyword, hybrid, llm"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get distribution of confidence scores in buckets

    Shows how suggestions are distributed across confidence ranges
    """
    return await SuggestionAnalytics.get_confidence_distribution(db, algorithm)


@router.get("/analytics/generation-trends", response_model=list[dict[str, Any]])
async def get_generation_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """
    Get daily suggestion generation trends

    Shows how many suggestions are being generated over time
    """
    return await SuggestionAnalytics.get_generation_trends(db, days)


@router.get("/analytics/review-velocity", response_model=dict[str, Any])
async def get_review_velocity(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get review velocity metrics

    Shows how quickly suggestions are being reviewed
    """
    return await SuggestionAnalytics.get_review_velocity(db, days)


@router.get("/analytics/algorithm-comparison", response_model=list[dict[str, Any]])
async def get_algorithm_comparison(db: AsyncSession = Depends(get_db)) -> list[dict[str, Any]]:
    """
    Compare all algorithms across multiple metrics

    Returns comprehensive comparison to inform algorithm selection
    """
    return await SuggestionAnalytics.get_algorithm_comparison(db)
