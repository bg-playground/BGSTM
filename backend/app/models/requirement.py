import enum
import uuid
from sqlalchemy import Column, String, Text, Enum, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin


class RequirementType(str, enum.Enum):
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    TECHNICAL = "technical"


class PriorityLevel(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RequirementStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    TESTED = "tested"
    CLOSED = "closed"


class Requirement(Base, TimestampMixin):
    __tablename__ = "requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, nullable=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    type = Column(Enum(RequirementType), nullable=False)
    priority = Column(Enum(PriorityLevel), nullable=False)
    status = Column(Enum(RequirementStatus), nullable=False, default=RequirementStatus.DRAFT)
    module = Column(String(100), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    metadata = Column(JSONB, nullable=True)
    source_system = Column(String(50), nullable=True)
    source_url = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    version = Column(Integer, default=1)

    # Relationships
    links = relationship("RequirementTestCaseLink", back_populates="requirement", cascade="all, delete-orphan")
    suggestions = relationship("LinkSuggestion", back_populates="requirement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Requirement(id={self.id}, external_id={self.external_id}, title={self.title[:50]})>"
