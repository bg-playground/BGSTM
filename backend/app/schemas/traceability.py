"""Schemas for traceability matrix and metrics"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class LinkedTestCase(BaseModel):
    """Test case linked to a requirement"""

    test_case_id: UUID
    title: str
    link_status: str  # 'accepted', 'pending', 'rejected'
    link_id: UUID
    link_type: str
    confidence_score: float | None = None

    model_config = ConfigDict(from_attributes=True)


class RequirementCoverage(BaseModel):
    """Coverage information for a single requirement"""

    requirement_id: UUID
    requirement_title: str
    external_id: str | None = None
    linked_test_cases: list[LinkedTestCase]
    coverage_status: str  # 'covered', 'partially_covered', 'uncovered'

    model_config = ConfigDict(from_attributes=True)


class OrphanTestCase(BaseModel):
    """Test case with no linked requirements"""

    test_case_id: UUID
    title: str
    external_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TraceabilityMatrixResponse(BaseModel):
    """Complete traceability matrix response"""

    coverage_percentage: float
    total_requirements: int
    covered_requirements: int
    uncovered_requirements: int
    total_test_cases: int
    orphan_test_cases: int
    matrix: list[RequirementCoverage]
    orphans: list[OrphanTestCase]

    model_config = ConfigDict(from_attributes=True)


class AlgorithmMetrics(BaseModel):
    """Metrics for a specific suggestion algorithm"""

    algorithm: str
    total_suggestions: int
    accepted_suggestions: int
    rejected_suggestions: int
    pending_suggestions: int
    acceptance_rate: float


class MetricsResponse(BaseModel):
    """Metrics response"""

    coverage_percentage: float
    suggestion_acceptance_rate: float
    total_requirements: int
    total_test_cases: int
    total_links: int
    total_suggestions: int
    accepted_suggestions: int
    rejected_suggestions: int
    pending_suggestions: int
    manual_links: int
    ai_suggested_links: int
    algorithm_breakdown: list[AlgorithmMetrics]

    model_config = ConfigDict(from_attributes=True)
