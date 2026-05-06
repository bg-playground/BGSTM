"""SQLAlchemy model for machine runner tokens (BGSTM#296)."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint

from .base import Base
from .requirement import GUID, ArrayType


class RunnerToken(Base):
    """A long-lived machine token issued to an external test runner.

    The plaintext token is **never** stored; only a salted SHA-256 hash is persisted.
    Tokens are prefixed with ``bgstm_runner_`` and can be individually revoked.
    """

    __tablename__ = "runner_tokens"
    __table_args__ = (UniqueConstraint("hashed_token", name="uq_runner_tokens_hashed_token"),)

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    hashed_token = Column(String(128), unique=True, nullable=False, index=True)
    salt = Column(String(64), nullable=False)
    label = Column(String(255), nullable=False)
    scopes = Column(ArrayType(), nullable=False)
    created_by_user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<RunnerToken(id={self.id}, label={self.label!r}, revoked={self.revoked_at is not None})>"
