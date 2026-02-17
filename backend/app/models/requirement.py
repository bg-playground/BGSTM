import enum
import json
import uuid

from sqlalchemy import ARRAY, Column, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.types import CHAR, TypeDecorator

from .base import Base, TimestampMixin


# UUID type that works with both PostgreSQL and SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36), storing as stringified hex values.
    """

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


# JSON type that works with both PostgreSQL and SQLite
class JSON(TypeDecorator):
    """Platform-independent JSON type.
    Uses PostgreSQL's JSONB type, otherwise uses TEXT for SQLite.
    """

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is not None and dialect.name != "postgresql":
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and dialect.name != "postgresql":
            value = json.loads(value)
        return value


# Array type that works with both PostgreSQL and SQLite
class ArrayType(TypeDecorator):
    """Platform-independent Array type.
    Uses PostgreSQL's ARRAY type, otherwise uses JSON-encoded TEXT for SQLite.
    """

    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(ARRAY(String))
        else:
            return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is not None and dialect.name != "postgresql":
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None and dialect.name != "postgresql":
            value = json.loads(value)
        return value


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

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, nullable=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text, nullable=False)
    type = Column(Enum(RequirementType), nullable=False)
    priority = Column(Enum(PriorityLevel), nullable=False)
    status = Column(Enum(RequirementStatus), nullable=False, default=RequirementStatus.DRAFT)
    module = Column(String(100), nullable=True)
    tags = Column(ArrayType(), nullable=True)
    custom_metadata = Column(JSON(), nullable=True)
    source_system = Column(String(50), nullable=True)
    source_url = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    version = Column(Integer, default=1)

    # Relationships
    links = relationship("RequirementTestCaseLink", back_populates="requirement", cascade="all, delete-orphan")
    suggestions = relationship("LinkSuggestion", back_populates="requirement", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Requirement(id={self.id}, external_id={self.external_id}, title={self.title[:50]})>"
