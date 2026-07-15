from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.crud import quality_metrics as crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.quality_metrics import (
    AutomationCoverageResponse,
    DefectsByModuleResponse,
    DefectTrendResponse,
    FlakyRankingResponse,
    PassRateTrendResponse,
    QualityDashboardSnapshot,
    SummaryStatsResponse,
)

router = APIRouter(prefix="/quality-metrics")

WindowParam = Literal[7, 30, 90]


@router.get("/", response_model=QualityDashboardSnapshot)
async def get_quality_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QualityDashboardSnapshot:
    _ = current_user
    return await crud.get_quality_dashboard_snapshot(db, 30)


@router.get("/defect-trend", response_model=DefectTrendResponse)
async def get_defect_trend(
    window: WindowParam = Query(30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DefectTrendResponse:
    _ = current_user
    return await crud.get_defect_trend(db, window)


@router.get("/pass-rate-trend", response_model=PassRateTrendResponse)
async def get_pass_rate_trend(
    window: WindowParam = Query(30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PassRateTrendResponse:
    _ = current_user
    return await crud.get_pass_rate_trend(db, window)


@router.get("/defects-by-module", response_model=DefectsByModuleResponse)
async def get_defects_by_module(
    window: WindowParam = Query(30),
    top_n: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DefectsByModuleResponse:
    _ = current_user
    return await crud.get_defects_by_module(db, window, top_n)


@router.get("/automation-coverage", response_model=AutomationCoverageResponse)
async def get_automation_coverage(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AutomationCoverageResponse:
    _ = current_user
    return await crud.get_automation_coverage(db)


@router.get("/flaky-ranking", response_model=FlakyRankingResponse)
async def get_flaky_ranking(
    window: WindowParam = Query(30),
    top_n: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FlakyRankingResponse:
    _ = current_user
    return await crud.get_flaky_ranking(db, window, top_n)


@router.get("/summary-stats", response_model=SummaryStatsResponse)
async def get_summary_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SummaryStatsResponse:
    _ = current_user
    return await crud.get_summary_stats(db)
