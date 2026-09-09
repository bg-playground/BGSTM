from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RecurringDefectEntry(BaseModel):
    test_case_id: UUID | None = None
    external_id: str | None = None
    display_name: str
    module: str
    failure_count: int
    cumulative_pct: float
    latest_failure_session_id: UUID
    latest_failure_at: datetime


class RecurringDefectsParetoResponse(BaseModel):
    entries: list[RecurringDefectEntry] = Field(default_factory=list)
    total_recurring_failures: int = 0
    is_synthetic: bool = False
    reason: str | None = None
