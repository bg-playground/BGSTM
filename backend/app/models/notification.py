"""Notification model"""

import enum
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.sql import func

from .base import Base
from .requirement import GUID, JSON


class NotificationType(str, enum.Enum):
    SUGGESTIONS_GENERATED = "suggestions_generated"
    COVERAGE_DROP = "coverage_drop"
    SUGGESTION_REVIEWED = "suggestion_reviewed"
    REQUIREMENT_CREATED = "requirement_created"
    TEST_CASE_CREATED = "test_case_created"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Boolean, default=False, nullable=False)
    metadata_ = Column("metadata", JSON(), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.type}, user_id={self.user_id})>"
