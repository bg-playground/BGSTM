"""SQLAlchemy model for External Case Results (BGSTM#303)."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Enum, ForeignKey, Index, Integer, String, Text, text

from .base import Base
from .requirement import GUID


def _enum_values(x):
    return [e.value for e in x]


def _utcnow():
    return datetime.now(tz=timezone.utc).replace(tzinfo=None)


class CaseStatus(str, enum.Enum):
    started = "started"
    passed = "passed"
    failed = "failed"
    skipped = "skipped"
    flaky = "flaky"
    aborted = "aborted"


class ExternalCaseResult(Base):
    __tablename__ = "external_case_results"
    __table_args__ = (
        CheckConstraint("duration_ms >= 0", name="ck_external_case_results_duration_ms_nonnegative"),
        Index("idx_external_case_results_session_id", "session_id"),
        Index(
            "uq_external_case_results_session_external_id",
            "session_id",
            "external_id",
            unique=True,
            postgresql_where=text("external_id IS NOT NULL"),
        ),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id = Column(GUID(), ForeignKey("external_run_sessions.id"), nullable=False)
    test_case_id = Column(GUID(), ForeignKey("test_cases.id"), nullable=True)
    external_id = Column(String(500), nullable=True)
    title = Column(String(500), nullable=False)
    outcome = Column(
        Enum(
            CaseStatus,
            name="case_outcome",
            values_callable=_enum_values,
            create_type=False,
        ),
        nullable=False,
    )
    duration_ms = Column(Integer, nullable=False)
    error_message = Column(Text, nullable=True)
    auto_registered = Column(Boolean, nullable=False, default=False, server_default="false")
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow, onupdate=_utcnow)
