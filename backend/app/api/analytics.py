"""API endpoints for Suggestion Analytics"""

import csv
import io
from typing import Any

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.crud import traceability as traceability_crud
from app.db.session import get_db
from app.models.user import User
from app.services.analytics import SuggestionAnalytics

router = APIRouter()


@router.get("/analytics/acceptance-rates", response_model=list[dict[str, Any]])
async def get_acceptance_rates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get acceptance/rejection rates for link suggestions over time.

    Returns monthly periods with counts of accepted, rejected, and pending
    suggestions along with the acceptance rate percentage.
    """
    analytics = SuggestionAnalytics(db)
    return await analytics.get_acceptance_rates()


@router.get("/analytics/confidence-distribution", response_model=list[dict[str, Any]])
async def get_confidence_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get distribution of confidence scores across suggestions.

    Returns counts and percentages for score ranges:
    0.0–0.2, 0.2–0.4, 0.4–0.6, 0.6–0.8, 0.8–1.0
    """
    analytics = SuggestionAnalytics(db)
    return await analytics.get_confidence_distribution()


@router.get("/analytics/generation-trends", response_model=list[dict[str, Any]])
async def get_generation_trends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get trends in suggestion generation volume over time.

    Returns monthly counts of suggestions created.
    """
    analytics = SuggestionAnalytics(db)
    return await analytics.get_generation_trends()


@router.get("/analytics/review-velocity", response_model=dict[str, Any])
async def get_review_velocity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get review velocity metrics — how quickly suggestions are being reviewed.

    Returns average and median review time (in hours) and total reviewed count.
    """
    analytics = SuggestionAnalytics(db)
    return await analytics.get_review_velocity()


@router.get("/analytics/algorithm-comparison", response_model=list[dict[str, Any]])
async def get_algorithm_comparison(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Compare performance metrics across algorithms (tfidf, keyword, hybrid, etc.).

    Returns per-algorithm counts, acceptance rates, and average confidence scores.
    """
    analytics = SuggestionAnalytics(db)
    return await analytics.get_algorithm_comparison()


@router.get("/metrics/export/csv")
async def export_metrics_csv(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export system metrics as CSV including coverage stats, suggestion counts by status,
    and algorithm breakdown.
    """
    metrics = await traceability_crud.get_metrics(db)

    output = io.StringIO()
    writer = csv.writer(output)

    # Coverage stats section
    writer.writerow(["Coverage Statistics"])
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Coverage Percentage", f"{metrics.coverage_percentage:.2f}%"])
    writer.writerow(["Total Requirements", metrics.total_requirements])
    writer.writerow(["Total Test Cases", metrics.total_test_cases])
    writer.writerow(["Total Links", metrics.total_links])
    writer.writerow(["Manual Links", metrics.manual_links])
    writer.writerow(["AI Suggested Links", metrics.ai_suggested_links])

    writer.writerow([])  # Separator

    # Suggestion counts by status
    writer.writerow(["Suggestion Counts by Status"])
    writer.writerow(["Status", "Count"])
    writer.writerow(["Total", metrics.total_suggestions])
    writer.writerow(["Accepted", metrics.accepted_suggestions])
    writer.writerow(["Rejected", metrics.rejected_suggestions])
    writer.writerow(["Pending", metrics.pending_suggestions])
    writer.writerow(["Suggestion Acceptance Rate", f"{metrics.suggestion_acceptance_rate:.2f}%"])

    writer.writerow([])  # Separator

    # Algorithm breakdown
    writer.writerow(["Algorithm Breakdown"])
    writer.writerow(["Algorithm", "Total", "Accepted", "Rejected", "Pending", "Acceptance Rate"])
    for algo in metrics.algorithm_breakdown:
        writer.writerow(
            [
                algo.algorithm,
                algo.total_suggestions,
                algo.accepted_suggestions,
                algo.rejected_suggestions,
                algo.pending_suggestions,
                f"{algo.acceptance_rate:.2f}%",
            ]
        )

    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=metrics.csv"},
    )
