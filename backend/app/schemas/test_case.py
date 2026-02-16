from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.models.test_case import TestCaseType, TestCaseStatus, AutomationStatus
from app.models.requirement import PriorityLevel


class TestCaseBase(BaseModel):
    """Base schema for TestCase"""
    title: str = Field(..., max_length=500)
    description: str
    type: TestCaseType
    priority: PriorityLevel
    status: TestCaseStatus = TestCaseStatus.DRAFT
    steps: Optional[Dict[str, Any]] = None
    preconditions: Optional[str] = None
    postconditions: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    module: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    automation_status: AutomationStatus = AutomationStatus.MANUAL
    execution_time_minutes: Optional[int] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    source_system: Optional[str] = Field(None, max_length=50)
    source_url: Optional[str] = None
    created_by: Optional[str] = Field(None, max_length=100)


class TestCaseCreate(TestCaseBase):
    """Schema for creating a TestCase"""
    external_id: Optional[str] = Field(None, max_length=100)


class TestCaseUpdate(BaseModel):
    """Schema for updating a TestCase"""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    type: Optional[TestCaseType] = None
    priority: Optional[PriorityLevel] = None
    status: Optional[TestCaseStatus] = None
    steps: Optional[Dict[str, Any]] = None
    preconditions: Optional[str] = None
    postconditions: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    module: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    automation_status: Optional[AutomationStatus] = None
    execution_time_minutes: Optional[int] = None
    custom_metadata: Optional[Dict[str, Any]] = None
    source_system: Optional[str] = Field(None, max_length=50)
    source_url: Optional[str] = None


class TestCaseResponse(TestCaseBase):
    """Schema for TestCase response"""
    id: UUID
    external_id: Optional[str]
    version: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
