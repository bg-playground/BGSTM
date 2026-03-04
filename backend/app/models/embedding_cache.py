"""EmbeddingCache model for persistent embedding storage"""

import uuid

from sqlalchemy import Column, Integer, String, UniqueConstraint

from .base import Base, TimestampMixin
from .requirement import GUID, JSON


class EmbeddingCache(Base, TimestampMixin):
    """Persistent cache for text embeddings to avoid redundant API calls across restarts."""

    __tablename__ = "embedding_cache"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    text_hash = Column(String(64), nullable=False, index=True)
    embedding = Column(JSON(), nullable=False)
    model_name = Column(String(200), nullable=False)
    provider = Column(String(50), nullable=False)
    dimensions = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint("text_hash", "model_name", name="uq_embedding_text_model"),)

    def __repr__(self):
        return f"<EmbeddingCache(text_hash={self.text_hash[:16]}…, model={self.model_name})>"
