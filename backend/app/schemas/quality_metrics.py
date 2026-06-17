from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class SeverityMix(BaseModel):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class DefectTrendPoint(BaseModel):
    date: date
    total: int
    by_severity: SeverityMix


class DefectTrendResponse(BaseModel):
    points: list[DefectTrendPoint] = Field(default_factory=list)
    is_synthetic: bool = False
    reason: str | None = None


class PassRateTrendPoint(BaseModel):
    date: date
    pass_rate_pct: float
    total_executed: int


class PassRateTrendResponse(BaseModel):
    points: list[PassRateTrendPoint] = Field(default_factory=list)
    is_synthetic: bool = False
    reason: str | None = None


class ModuleQualityBucket(BaseModel):
    module: str
    count: int
    severity_mix: SeverityMix


class DefectsByModuleResponse(BaseModel):
    modules: list[ModuleQualityBucket] = Field(default_factory=list)
    is_synthetic: bool = False
    reason: str | None = None


class AutomationCoverageResponse(BaseModel):
    total: int
    automated: int
    manual: int
    in_progress: int
    percent_automated: float
    reason: str | None = None


class SummaryStatsResponse(BaseModel):
    defect_removal_efficiency_pct: float | None = None
    defect_removal_efficiency_reason: str | None = None
    mean_time_to_repair_hours: float | None = None
    mean_time_to_repair_hours_reason: str | None = None
    escape_rate_pct: float | None = None
    escape_rate_pct_reason: str | None = None
    total_defects_30d: int
    open_critical_defects: int


class QualityDashboardSnapshot(BaseModel):
    generated_at: datetime
    window_days: int
    defect_trend: DefectTrendResponse
    pass_rate_trend: PassRateTrendResponse
    defects_by_module: DefectsByModuleResponse
    automation_coverage: AutomationCoverageResponse
    summary_stats: SummaryStatsResponse
