from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: UUID
    actor_kind: str
    user_id: UUID | None
    actor_token_id: UUID | None
    action: str
    resource_type: str
    resource_id: str
    details: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    entries: list[AuditLogResponse]
    total: int
