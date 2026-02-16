import enum
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Enum, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base
from .requirement import GUID  # Import cross-platform GUID type


class LinkType(str, enum.Enum):
    COVERS = "covers"
    VERIFIES = "verifies"
    VALIDATES = "validates"
    RELATED = "related"


class LinkSource(str, enum.Enum):
    MANUAL = "manual"
    AI_SUGGESTED = "ai_suggested"
    AI_CONFIRMED = "ai_confirmed"
    IMPORTED = "imported"


class RequirementTestCaseLink(Base):
    __tablename__ = "requirement_test_case_links"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    requirement_id = Column(GUID(), ForeignKey("requirements.id", ondelete="CASCADE"), nullable=False)
    test_case_id = Column(GUID(), ForeignKey("test_cases.id", ondelete="CASCADE"), nullable=False)
    link_type = Column(Enum(LinkType), nullable=False, default=LinkType.COVERS)
    confidence_score = Column(Float, nullable=True)
    link_source = Column(Enum(LinkSource), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    confirmed_by = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    requirement = relationship("Requirement", back_populates="links")
    test_case = relationship("TestCase", back_populates="links")

    __table_args__ = (
        UniqueConstraint('requirement_id', 'test_case_id', name='uq_requirement_test_case'),
    )

    def __repr__(self):
        return f"<Link(req={self.requirement_id}, tc={self.test_case_id}, source={self.link_source})>"
