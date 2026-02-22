"""AuditLog model"""

import uuid

from sqlalchemy import Column, ForeignKey, String

from .base import Base, TimestampMixin
from .requirement import GUID, JSON


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_log"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON(), nullable=True)

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource_type={self.resource_type})>"
