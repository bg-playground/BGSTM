"""Pydantic schemas for the External Results API (v1).

This module defines the request/response shapes for external test runners
reporting execution results into BGSTM. It is a types-only module — no
FastAPI imports, no database access.

Canonical spec: docs/specs/external_results_v1.md
Tracking: BGSTM#291 (parent epic), BGSTM#299 (this spec)
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class RunStatus(str, Enum):
    """Lifecycle status for an external test session."""

    started = "started"
    passed = "passed"
    failed = "failed"
    skipped = "skipped"
    aborted = "aborted"


class CaseOutcome(str, Enum):
    """Outcome for an individual test-case result."""

    passed = "passed"
    failed = "failed"
    skipped = "skipped"
    flaky = "flaky"


class ArtifactKind(str, Enum):
    """Type of binary artifact attached to a case result."""

    screenshot = "screenshot"
    trace = "trace"
    video = "video"
    log = "log"
    other = "other"


# ---------------------------------------------------------------------------
# Session models
# ---------------------------------------------------------------------------

_SESSION_EXAMPLE: dict[str, Any] = {
    "runner": "@bgstm/playwright-core@0.1.0",
    "project_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "git_sha": "abc123def456",
    "git_branch": "main",
    "ci_url": "https://github.com/org/repo/actions/runs/123",
    "metadata": {"os": "ubuntu-22.04", "node": "20.11.0"},
}


class SessionCreate(BaseModel):
    """Payload for ``POST /api/v1/external-results/session``."""

    model_config = ConfigDict(
        json_schema_extra={"example": _SESSION_EXAMPLE},
    )

    runner: str = Field(..., description="Identifier of the test runner (name + version).")
    project_id: UUID = Field(..., description="BGSTM project this session belongs to.")
    git_sha: str | None = Field(None, description="Full or short commit SHA being tested.")
    git_branch: str | None = Field(None, description="Branch name under test.")
    ci_url: HttpUrl | None = Field(None, description="URL of the CI job that triggered this run.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary key/value runner metadata.")


class SessionResponse(BaseModel):
    """Response body for session endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: RunStatus
    started_at: datetime
    finished_at: datetime | None = None
    runner: str
    project_id: UUID
    git_sha: str | None = None
    git_branch: str | None = None
    ci_url: HttpUrl | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


_TERMINAL_STATUSES = {RunStatus.passed, RunStatus.failed, RunStatus.aborted}


class SessionFinish(BaseModel):
    """Payload for ``PATCH /api/v1/external-results/session/{session_id}``."""

    status: RunStatus = Field(..., description="Terminal status for the session.")
    summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Aggregate counters, e.g. ``{total: 42, failed: 2}``.",
        examples=[{"total": 42, "failed": 2}],
    )

    @model_validator(mode="after")
    def _validate_terminal_status(self) -> SessionFinish:
        if self.status not in _TERMINAL_STATUSES:
            raise ValueError(
                f"SessionFinish.status must be one of "
                f"{[s.value for s in _TERMINAL_STATUSES]}, got '{self.status.value}'."
            )
        return self


# ---------------------------------------------------------------------------
# Case result models
# ---------------------------------------------------------------------------


class CaseResultCreate(BaseModel):
    """Payload for ``POST /api/v1/external-results/case``."""

    session_id: UUID = Field(..., description="Session this result belongs to.")
    test_case_id: UUID | None = Field(None, description="BGSTM test-case UUID, if known.")
    external_id: str | None = Field(
        None,
        description="Runner-assigned identifier (e.g. full test title). "
        "Duplicate external_id within the same session collapses to the same row.",
    )
    title: str = Field(..., description="Human-readable test title.")
    outcome: CaseOutcome
    duration_ms: int = Field(..., ge=0, description="Wall-clock duration in milliseconds.")
    error_message: str | None = Field(None, description="First error line or assertion message.")
    requirement_ids: list[UUID] = Field(
        default_factory=list,
        description="Requirement UUIDs to link; duplicate insertion is a no-op.",
    )

    @model_validator(mode="after")
    def _require_at_least_one_id(self) -> CaseResultCreate:
        if self.test_case_id is None and self.external_id is None:
            raise ValueError("At least one of 'test_case_id' or 'external_id' must be provided.")
        return self


class CaseResultResponse(BaseModel):
    """Response body for case-result endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    test_case_id: UUID | None = None
    external_id: str | None = None
    title: str
    outcome: CaseOutcome
    duration_ms: int = Field(..., ge=0)
    error_message: str | None = None
    requirement_ids: list[UUID] = Field(default_factory=list)
    created_at: datetime
    auto_registered: bool = Field(
        False,
        description="True when BGSTM created a new test-case record from external_id.",
    )


class CaseResultUpdate(BaseModel):
    """Payload for ``PATCH /api/v1/external-results/case/{id}``."""

    outcome: CaseOutcome | None = None
    duration_ms: int | None = Field(None, ge=0)
    error_message: str | None = None


# ---------------------------------------------------------------------------
# Artifact models
# ---------------------------------------------------------------------------


class ArtifactCreate(BaseModel):
    """Payload for ``POST /api/v1/external-results/artifact`` (multipart metadata part)."""

    case_result_id: UUID = Field(..., description="Case result this artifact belongs to.")
    kind: ArtifactKind
    filename: str = Field(..., description="Original filename, including extension.")
    content_type: str = Field(..., description="MIME type, e.g. ``image/png``.")
    size_bytes: int = Field(..., ge=0, description="Byte length of the artifact body.")


class ArtifactResponse(ArtifactCreate):
    """Response body for artifact endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: HttpUrl = Field(..., description="Presigned or permanent download URL.")
    uploaded_at: datetime


# ---------------------------------------------------------------------------
# Error model
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    """Unified error envelope returned by all External Results endpoints."""

    code: str = Field(..., description="Machine-readable error code, e.g. ``runner_token.invalid``.")
    message: str = Field(..., description="Human-readable error description.")
    details: dict[str, Any] | None = Field(None, description="Optional structured detail map.")
