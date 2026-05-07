import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String
from sqlalchemy.sql import func

from .base import Base
from .requirement import GUID, JSON


class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = (
        CheckConstraint(
            "(actor_kind = 'user' AND user_id IS NOT NULL AND actor_token_id IS NULL) "
            "OR (actor_kind = 'runner_token' AND actor_token_id IS NOT NULL AND user_id IS NULL)",
            name="ck_audit_log_actor_identity",
        ),
        Index("idx_audit_log_actor_kind_created_at", "actor_kind", "created_at"),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    actor_kind = Column(String(20), nullable=False, server_default="user")
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=True, index=True)
    actor_token_id = Column(
        GUID(),
        ForeignKey("runner_tokens.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(36), nullable=False)
    details = Column(JSON(), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource_type={self.resource_type})>"
