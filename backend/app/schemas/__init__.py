"""Pydantic schemas for BGSTM AI Traceability"""

from .link import (
    BulkReviewRequest,
    LinkCreate,
    LinkResponse,
    SuggestionCreate,
    SuggestionResponse,
    SuggestionReview,
)
from .quality_metrics import (
    AutomationCoverageResponse,
    DefectsByModuleResponse,
    DefectTrendPoint,
    DefectTrendResponse,
    ModuleQualityBucket,
    PassRateTrendPoint,
    PassRateTrendResponse,
    QualityDashboardSnapshot,
    SeverityMix,
    SummaryStatsResponse,
)
from .release_readiness import ReadinessCriterion, ReadinessSnapshot, ReadinessSummary, RoleSignoff, SignoffRequest
from .requirement import RequirementCreate, RequirementResponse, RequirementUpdate
from .test_case import TestCaseCreate, TestCaseResponse, TestCaseUpdate

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
    "BulkReviewRequest",
    "SeverityMix",
    "DefectTrendPoint",
    "DefectTrendResponse",
    "PassRateTrendPoint",
    "PassRateTrendResponse",
    "ModuleQualityBucket",
    "DefectsByModuleResponse",
    "AutomationCoverageResponse",
    "SummaryStatsResponse",
    "QualityDashboardSnapshot",
    "ReadinessCriterion",
    "RoleSignoff",
    "ReadinessSummary",
    "ReadinessSnapshot",
    "SignoffRequest",
]
