from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.requirement import PriorityLevel, RequirementStatus, RequirementType


class RequirementBase(BaseModel):
    """Base schema for Requirement"""

    title: str = Field(..., max_length=500)
    description: str
    type: RequirementType
    priority: PriorityLevel
    status: RequirementStatus = RequirementStatus.DRAFT
    module: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    custom_metadata: dict[str, Any] | None = None
    source_system: str | None = Field(None, max_length=50)
    source_url: str | None = None
    created_by: str | None = Field(None, max_length=100)


class RequirementCreate(RequirementBase):
    """Schema for creating a Requirement"""

    external_id: str | None = Field(None, max_length=100)


class RequirementUpdate(BaseModel):
    """Schema for updating a Requirement"""

    title: str | None = Field(None, max_length=500)
    description: str | None = None
    type: RequirementType | None = None
    priority: PriorityLevel | None = None
    status: RequirementStatus | None = None
    module: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    custom_metadata: dict[str, Any] | None = None
    source_system: str | None = Field(None, max_length=50)
    source_url: str | None = None


class RequirementResponse(RequirementBase):
    """Schema for Requirement response"""

    id: UUID
    external_id: str | None
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
