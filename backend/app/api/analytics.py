"""FastAPI router for analytics endpoints"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.analytics import SuggestionAnalytics

router = APIRouter()


@router.get("/acceptance-rates")
async def get_acceptance_rates(
    time_period: Optional[str] = Query(None, description="ISO-8601 date string; filter suggestions created on or after this date"),
    db: AsyncSession = Depends(get_db),
):
    """Get suggestion acceptance, rejection, and pending rates."""
    return await SuggestionAnalytics.get_acceptance_rates(db, time_period=time_period)


@router.get("/confidence-distribution")
async def get_confidence_distribution(
    algorithm: Optional[str] = Query(None, description="Filter by suggestion method (e.g. keyword_match)"),
    db: AsyncSession = Depends(get_db),
):
    """Get distribution of similarity scores, optionally filtered by algorithm."""
    return await SuggestionAnalytics.get_confidence_distribution(db, algorithm=algorithm)


@router.get("/generation-trends")
async def get_generation_trends(
    days: int = Query(30, ge=1, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
):
    """Get suggestion generation trends over the specified number of days."""
    return await SuggestionAnalytics.get_generation_trends(db, days=days)


@router.get("/review-velocity")
async def get_review_velocity(
    days: int = Query(30, ge=1, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
):
    """Get review velocity (time from creation to review) over the specified number of days."""
    return await SuggestionAnalytics.get_review_velocity(db, days=days)


@router.get("/algorithm-comparison")
async def get_algorithm_comparison(
    db: AsyncSession = Depends(get_db),
):
    """Compare performance across different suggestion algorithms."""
    return await SuggestionAnalytics.get_algorithm_comparison(db)
