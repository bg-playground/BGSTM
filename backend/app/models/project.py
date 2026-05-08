import uuid

from sqlalchemy import Column, String, Text

from .base import Base, TimestampMixin
from .requirement import GUID


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name!r})>"
