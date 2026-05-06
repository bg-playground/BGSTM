"""SQLAlchemy model for External Run Sessions (BGSTM#300)."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String

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
