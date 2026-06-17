import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, Text

from .base import Base, TimestampMixin
from .requirement import GUID, _enum_values


class ReleaseSignoffRole(str, enum.Enum):
    qa_lead = "qa_lead"
    product = "product"
    eng_lead = "eng_lead"


class ReleaseSignoff(Base, TimestampMixin):
    __tablename__ = "release_signoffs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    role = Column(
        Enum(ReleaseSignoffRole, values_callable=_enum_values, name="releasesignoffrole", create_type=False),
        nullable=False,
    )
    signed_off_by_user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    signed_off_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    note = Column(Text, nullable=True)
    revoked_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_release_signoffs_role", "role"),
        Index("idx_release_signoffs_revoked_at", "revoked_at"),
    )
