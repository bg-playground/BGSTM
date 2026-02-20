from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.requirement import PriorityLevel
from app.models.test_case import AutomationStatus, TestCaseStatus, TestCaseType


class TestCaseBase(BaseModel):
    """Base schema for TestCase"""

    title: str = Field(..., max_length=500)
    description: str
    type: TestCaseType
    priority: PriorityLevel
    status: TestCaseStatus = TestCaseStatus.DRAFT
    steps: dict[str, Any] | None = None
    preconditions: str | None = None
    postconditions: str | None = None
    test_data: dict[str, Any] | None = None
    module: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    automation_status: AutomationStatus = AutomationStatus.MANUAL
    execution_time_minutes: int | None = None
    custom_metadata: dict[str, Any] | None = None
    source_system: str | None = Field(None, max_length=50)
    source_url: str | None = None
    created_by: str | None = Field(None, max_length=100)


class TestCaseCreate(TestCaseBase):
    """Schema for creating a TestCase"""

    external_id: str | None = Field(None, max_length=100)


class TestCaseUpdate(BaseModel):
    """Schema for updating a TestCase"""

    title: str | None = Field(None, max_length=500)
    description: str | None = None
    type: TestCaseType | None = None
    priority: PriorityLevel | None = None
    status: TestCaseStatus | None = None
    steps: dict[str, Any] | None = None
    preconditions: str | None = None
    postconditions: str | None = None
    test_data: dict[str, Any] | None = None
    module: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    automation_status: AutomationStatus | None = None
    execution_time_minutes: int | None = None
    custom_metadata: dict[str, Any] | None = None
    source_system: str | None = Field(None, max_length=50)
    source_url: str | None = None


class TestCaseResponse(TestCaseBase):
    """Schema for TestCase response"""

    id: UUID
    external_id: str | None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
