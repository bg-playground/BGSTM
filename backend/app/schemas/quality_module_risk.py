from __future__ import annotations

from pydantic import BaseModel, Field


class ModuleCoverageFailurePoint(BaseModel):
    module: str
    coverage_pct: float
    failure_density_pct: float
    total_requirements: int
    covered_requirements: int
    total_executions: int
    total_failures: int


class ModuleCoverageFailureResponse(BaseModel):
    points: list[ModuleCoverageFailurePoint] = Field(default_factory=list)
    median_coverage_pct: float | None = None
    median_failure_density_pct: float | None = None
    is_synthetic: bool = False
    reason: str | None = None
