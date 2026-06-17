from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ReadinessCriterion(BaseModel):
    id: str
    label: str
    status: Literal["pass", "fail", "warn", "na"]
    value: str
    threshold: str
    category: str


class RoleSignoff(BaseModel):
    role: str
    signed_off: bool
    signed_off_by: str | None
    signed_off_at: datetime | None
    note: str | None


class ReadinessSummary(BaseModel):
    total: int
    passed: int
    failed: int
    warning: int


class ReadinessSnapshot(BaseModel):
    overall_status: Literal["go", "no_go", "caution"]
    generated_at: datetime
    criteria: list[ReadinessCriterion]
    signoffs: list[RoleSignoff]
    summary: ReadinessSummary


class SignoffRequest(BaseModel):
    role: str
    note: str | None = None
