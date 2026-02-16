"""Pydantic schemas for BGSTM AI Traceability"""

from .requirement import RequirementCreate, RequirementUpdate, RequirementResponse
from .test_case import TestCaseCreate, TestCaseUpdate, TestCaseResponse
from .link import (
    LinkCreate,
    LinkResponse,
    SuggestionCreate,
    SuggestionResponse,
    SuggestionReview,
)

__all__ = [
    "RequirementCreate",
    "RequirementUpdate",
    "RequirementResponse",
    "TestCaseCreate",
    "TestCaseUpdate",
    "TestCaseResponse",
    "LinkCreate",
    "LinkResponse",
    "SuggestionCreate",
    "SuggestionResponse",
    "SuggestionReview",
]
