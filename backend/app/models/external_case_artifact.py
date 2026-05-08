"""SQLAlchemy model for External Case Artifacts (BGSTM#298)."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String

from .base import Base
from .requirement import GUID


def _enum_values(x):
    return [e.value for e in x]


def _utcnow():
    return datetime.now(tz=timezone.utc).replace(tzinfo=None)


class ArtifactKind(str, enum.Enum):
    screenshot = "screenshot"
    video = "video"
    trace = "trace"
    log = "log"
    other = "other"


class ExternalCaseArtifact(Base):
    __tablename__ = "external_case_artifacts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    case_result_id = Column(
        GUID(),
        ForeignKey("external_case_results.id", ondelete="CASCADE", name="fk_external_case_artifacts_case_result_id"),
        nullable=False,
        index=True,
    )
    kind = Column(
        Enum(
            ArtifactKind,
            name="artifact_kind",
            values_callable=_enum_values,
            create_type=False,
        ),
        nullable=False,
    )
    filename = Column(String(500), nullable=False)
    content_type = Column(String(200), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    storage_key = Column(String(1000), nullable=False)
    url = Column(String(2000), nullable=False)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
