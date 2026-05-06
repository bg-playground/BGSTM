"""SQLAlchemy models for External Results entities."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint

from .base import Base
from .requirement import GUID, JSON


def _enum_values(x):
    return [e.value for e in x]


class RunStatus(str, enum.Enum):
    """Lifecycle status for an external test session."""

    started = "started"
    passed = "passed"
    failed = "failed"
    skipped = "skipped"
    aborted = "aborted"


class CaseOutcome(str, enum.Enum):
    """Outcome for an individual external test-case result."""

    passed = "passed"
    failed = "failed"
    skipped = "skipped"
    flaky = "flaky"


def _utcnow():
    return datetime.now(tz=timezone.utc).replace(tzinfo=None)


class ExternalRunSession(Base):
    """Represents a single test-runner execution session.

    Created by a runner at suite start (POST /external-results/session) and
    closed with a terminal status (PATCH /external-results/session/{id}).
    """

    __tablename__ = "external_run_sessions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), nullable=False, index=True)
    runner = Column(String(255), nullable=False)
    status = Column(
        Enum(RunStatus, values_callable=_enum_values),
        nullable=False,
        default=RunStatus.started,
    )
    git_sha = Column(String(255), nullable=True)
    git_branch = Column(String(255), nullable=True)
    ci_url = Column(String(2048), nullable=True)
    run_metadata = Column(JSON(), nullable=True)
    started_at = Column(DateTime, default=_utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    summary = Column(JSON(), nullable=True)
    created_by_runner_token_id = Column(GUID(), ForeignKey("runner_tokens.id"), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<ExternalRunSession(id={self.id}, status={self.status}, runner={self.runner!r})>"


class ExternalCaseResult(Base):
    """Represents one test-case execution result reported by an external runner."""

    __tablename__ = "external_case_results"
    __table_args__ = (
        UniqueConstraint("project_id", "external_id", name="uq_external_case_results_project_external_id"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id = Column(GUID(), ForeignKey("external_run_sessions.id"), nullable=False, index=True)
    project_id = Column(GUID(), nullable=False, index=True)
    test_case_id = Column(GUID(), ForeignKey("test_cases.id"), nullable=True)
    external_id = Column(String(500), nullable=True)
    title = Column(String(500), nullable=False)
    outcome = Column(Enum(CaseOutcome, values_callable=_enum_values), nullable=False)
    duration_ms = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<ExternalCaseResult(id={self.id}, session_id={self.session_id}, outcome={self.outcome})>"
