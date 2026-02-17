from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.link import LinkSource, LinkType
from app.models.suggestion import SuggestionMethod, SuggestionStatus


class LinkBase(BaseModel):
    """Base schema for Link"""

    requirement_id: UUID
    test_case_id: UUID
    link_type: LinkType = LinkType.COVERS
    confidence_score: Optional[float] = None
    notes: Optional[str] = None


class LinkCreate(LinkBase):
    """Schema for creating a Link"""

    link_source: LinkSource = LinkSource.MANUAL
    created_by: Optional[str] = Field(None, max_length=100)


class LinkResponse(LinkBase):
    """Schema for Link response"""

    id: UUID
    link_source: LinkSource
    created_at: datetime
    created_by: Optional[str]
    confirmed_at: Optional[datetime]
    confirmed_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class SuggestionBase(BaseModel):
    """Base schema for LinkSuggestion"""

    requirement_id: UUID
    test_case_id: UUID
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    suggestion_method: SuggestionMethod
    suggestion_reason: Optional[str] = None
    suggestion_metadata: Optional[Dict[str, Any]] = None


class SuggestionCreate(SuggestionBase):
    """Schema for creating a LinkSuggestion"""

    pass


class SuggestionResponse(SuggestionBase):
    """Schema for LinkSuggestion response"""

    id: UUID
    status: SuggestionStatus
    created_at: datetime
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[str]
    feedback: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class SuggestionReview(BaseModel):
    """Schema for reviewing a suggestion"""

    status: SuggestionStatus
    feedback: Optional[str] = None
    reviewed_by: Optional[str] = Field(None, max_length=100)


class BatchSuggestionReview(BaseModel):
    """Schema for batch reviewing suggestions"""

    suggestion_ids: List[UUID]
    status: SuggestionStatus
    reviewed_by: Optional[str] = Field(None, max_length=100)
    feedback: Optional[str] = None


class BatchReviewResult(BaseModel):
    """Schema for batch review result"""

    total: int
    accepted: int
    rejected: int
    failed: int
    errors: List[str] = []
