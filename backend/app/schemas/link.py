from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.link import LinkType, LinkSource
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
