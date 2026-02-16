from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.requirement import RequirementType, PriorityLevel, RequirementStatus


class RequirementBase(BaseModel):
    """Base schema for Requirement"""
    title: str = Field(..., max_length=500)
    description: str
    type: RequirementType
    priority: PriorityLevel
    status: RequirementStatus = RequirementStatus.DRAFT
    module: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    source_system: Optional[str] = Field(None, max_length=50)
    source_url: Optional[str] = None
    created_by: Optional[str] = Field(None, max_length=100)


class RequirementCreate(RequirementBase):
    """Schema for creating a Requirement"""
    external_id: Optional[str] = Field(None, max_length=100)


class RequirementUpdate(BaseModel):
    """Schema for updating a Requirement"""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    type: Optional[RequirementType] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[RequirementStatus] = None
    module: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    source_system: Optional[str] = Field(None, max_length=50)
    source_url: Optional[str] = None


class RequirementResponse(RequirementBase):
    """Schema for Requirement response"""
    id: UUID
    external_id: Optional[str]
    version: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
