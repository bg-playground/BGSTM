"""Schemas for AuditLog"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: UUID
    user_id: UUID | None
    action: str
    resource_type: str
    resource_id: str | None
    details: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    skip: int
    limit: int
