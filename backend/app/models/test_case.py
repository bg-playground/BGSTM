import enum
import uuid
from sqlalchemy import Column, String, Text, Enum, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
from .requirement import PriorityLevel  # Reuse


class TestCaseType(str, enum.Enum):
    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UI = "ui"
    REGRESSION = "regression"


class TestCaseStatus(str, enum.Enum):
    DRAFT = "draft"
    READY = "ready"
    EXECUTING = "executing"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    DEPRECATED = "deprecated"


class AutomationStatus(str, enum.Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"
    AUTOMATABLE = "automatable"


class TestCase(Base, TimestampMixin):
    __tablename__ = "test_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, nullable=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    type = Column(Enum(TestCaseType), nullable=False)
    priority = Column(Enum(PriorityLevel), nullable=False)
    status = Column(Enum(TestCaseStatus), nullable=False, default=TestCaseStatus.DRAFT)
    steps = Column(JSONB, nullable=True)
    preconditions = Column(Text, nullable=True)
    postconditions = Column(Text, nullable=True)
    test_data = Column(JSONB, nullable=True)
    module = Column(String(100), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    automation_status = Column(Enum(AutomationStatus), default=AutomationStatus.MANUAL)
    execution_time_minutes = Column(Integer, nullable=True)
    metadata = Column(JSONB, nullable=True)
    source_system = Column(String(50), nullable=True)
    source_url = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    version = Column(Integer, default=1)

    # Relationships
    links = relationship("RequirementTestCaseLink", back_populates="test_case", cascade="all, delete-orphan")
    suggestions = relationship("LinkSuggestion", back_populates="test_case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestCase(id={self.id}, external_id={self.external_id}, title={self.title[:50]})>"
