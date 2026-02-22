import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from .base import Base
from .requirement import GUID, JSON


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(36), nullable=False)
    details = Column(JSON(), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource_type={self.resource_type})>"
