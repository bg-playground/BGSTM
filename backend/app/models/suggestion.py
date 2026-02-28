import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import relationship

from .base import Base
from .requirement import GUID, JSON  # Import cross-platform types


class SuggestionMethod(str, enum.Enum):
    SEMANTIC_SIMILARITY = "semantic_similarity"
    KEYWORD_MATCH = "keyword_match"
    HEURISTIC = "heuristic"
    HYBRID = "hybrid"
    LLM_EMBEDDING = "llm_embedding"


class SuggestionStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class LinkSuggestion(Base):
    __tablename__ = "link_suggestions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    requirement_id = Column(GUID(), ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False)
    test_case_id = Column(GUID(), ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    suggestion_method = Column(Enum(SuggestionMethod, values_callable=lambda x: [e.value for e in x]), nullable=False)
    suggestion_reason = Column(Text, nullable=True)
    suggestion_metadata = Column(JSON(), nullable=True)
    status = Column(Enum(SuggestionStatus, values_callable=lambda x: [e.value for e in x]), nullable=False, default=SuggestionStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    feedback = Column(Text, nullable=True)

    # Relationships
    requirement = relationship("Requirement", back_populates="suggestions")
    test_case = relationship("TestCase", back_populates="suggestions")

    __table_args__ = (
        Index("idx_suggestions_req_tc", "requirement_id", "test_case_id"),
        Index("idx_suggestions_similarity_score", "similarity_score"),
        Index("idx_suggestions_method", "suggestion_method"),
        Index("idx_suggestions_status_score", "status", "similarity_score"),
    )

    def __repr__(self):
        return f"<Suggestion(req={self.requirement_id}, tc={self.test_case_id}, score={self.similarity_score:.2f})>"
