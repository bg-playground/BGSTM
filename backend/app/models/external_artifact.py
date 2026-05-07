"""SQLAlchemy model for external case artifacts (BGSTM#298)."""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, String

from .base import Base
from .requirement import GUID


def _enum_values(x):
    return [e.value for e in x]


class ArtifactKind(str, enum.Enum):
    """Type of binary artifact attached to a case result."""

    screenshot = "screenshot"
    trace = "trace"
    video = "video"
    log = "log"
    other = "other"


def _utcnow():
    return datetime.now(tz=timezone.utc).replace(tzinfo=None)


class ExternalCaseArtifact(Base):
    """Stores metadata for an artifact uploaded by an external test runner.

    The binary is stored externally (local filesystem or S3); only the metadata
    and a URL pointer are persisted here.
    """

    __tablename__ = "external_case_artifacts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    case_result_id = Column(GUID(), ForeignKey("external_case_results.id", ondelete="CASCADE"), nullable=False)
    kind = Column(Enum(ArtifactKind, values_callable=_enum_values), nullable=False)
    filename = Column(String(500), nullable=False)
    content_type = Column(String(255), nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    storage_key = Column(String(1024), nullable=False, unique=True)
    url = Column(String(2048), nullable=False)
    uploaded_at = Column(DateTime, default=_utcnow, nullable=False)
    runner_token_id = Column(GUID(), ForeignKey("runner_tokens.id"), nullable=False)

    def __repr__(self) -> str:
        return f"<ExternalCaseArtifact(id={self.id}, kind={self.kind}, filename={self.filename!r})>"
