import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String

from .base import Base
from .requirement import GUID, JSON


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    details = Column(JSON(), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
