from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.link import LinkSource, LinkType
from app.models.suggestion import SuggestionMethod, SuggestionStatus


class LinkBase(BaseModel):
    """Base schema for Link"""

    requirement_id: UUID
    test_case_id: UUID
    link_type: LinkType = LinkType.COVERS
    confidence_score: float | None = None
    notes: str | None = None


class LinkCreate(LinkBase):
    """Schema for creating a Link"""

    link_source: LinkSource = LinkSource.MANUAL
    created_by: str | None = Field(None, max_length=100)


class LinkResponse(LinkBase):
    """Schema for Link response"""

    id: UUID
    link_source: LinkSource
    created_at: datetime
    created_by: str | None
    confirmed_at: datetime | None
    confirmed_by: str | None

    model_config = ConfigDict(from_attributes=True)


class SuggestionBase(BaseModel):
    """Base schema for LinkSuggestion"""

    requirement_id: UUID
    test_case_id: UUID
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    suggestion_method: SuggestionMethod
    suggestion_reason: str | None = None
    suggestion_metadata: dict[str, Any] | None = None


class SuggestionCreate(SuggestionBase):
    """Schema for creating a LinkSuggestion"""

    pass


class SuggestionResponse(SuggestionBase):
    """Schema for LinkSuggestion response"""

    id: UUID
    status: SuggestionStatus
    created_at: datetime
    reviewed_at: datetime | None
    reviewed_by: str | None
    feedback: str | None

    model_config = ConfigDict(from_attributes=True)


class SuggestionReview(BaseModel):
    """Schema for reviewing a suggestion"""

    status: SuggestionStatus
    feedback: str | None = None
    reviewed_by: str | None = Field(None, max_length=100)


class BulkReviewRequest(BaseModel):
    """Schema for bulk suggestion review"""

    suggestion_ids: list[UUID] = Field(..., min_length=1, max_length=100)
    status: SuggestionStatus
    feedback: str | None = None
    reviewed_by: str | None = Field(None, max_length=100)
