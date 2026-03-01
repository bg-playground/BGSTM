import enum
import uuid

from sqlalchemy import Column, Enum, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin
from .requirement import (  # Reuse and import common types
    GUID,
    JSON,
    ArrayType,
    PriorityLevel,
)


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

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, nullable=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    type = Column(Enum(TestCaseType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    priority = Column(Enum(PriorityLevel, values_callable=lambda x: [e.value for e in x]), nullable=False)
    status = Column(
        Enum(TestCaseStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=TestCaseStatus.DRAFT,
    )
    steps = Column(JSON(), nullable=True)
    preconditions = Column(Text, nullable=True)
    postconditions = Column(Text, nullable=True)
    test_data = Column(JSON(), nullable=True)
    module = Column(String(100), nullable=True)
    tags = Column(ArrayType(), nullable=True)
    automation_status = Column(
        Enum(AutomationStatus, values_callable=lambda x: [e.value for e in x]),
        default=AutomationStatus.MANUAL,
    )
    execution_time_minutes = Column(Integer, nullable=True)
    custom_metadata = Column(JSON(), nullable=True)
    source_system = Column(String(50), nullable=True)
    source_url = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    version = Column(Integer, default=1)

    # Relationships
    links = relationship("RequirementTestCaseLink", back_populates="test_case", cascade="all, delete-orphan")
    suggestions = relationship("LinkSuggestion", back_populates="test_case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TestCase(id={self.id}, external_id={self.external_id}, title={self.title[:50]})>"
