from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


RecoveryGroupBy = Literal["overall", "module", "severity"]


class RecoveryTrendPoint(BaseModel):
    date: date
    group: str
    mean_recovery_hours: float
    resolved_episodes: int


class RecoveryTrendResponse(BaseModel):
    window_days: int
    group_by: RecoveryGroupBy
    points: list[RecoveryTrendPoint] = Field(default_factory=list)
    mean_recovery_hours: float | None = None
    resolved_episodes: int = 0
    open_episodes: int = 0
    is_synthetic: bool = False
    reason: str | None = None
