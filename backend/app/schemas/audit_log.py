import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


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

    @field_validator("details", mode="before")
    @classmethod
    def _normalize_details(cls, value: Any) -> dict[str, Any] | None:
        if value is None or isinstance(value, dict):
            return value

        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                # Preserve invalid historical payloads as structured data instead of
                # failing audit-log reads for the entire response page.
                return {"raw": value}
            if isinstance(parsed, dict):
                return parsed
            return {"value": parsed}

        return {"value": value}


class AuditLogListResponse(BaseModel):
    entries: list[AuditLogResponse]
    total: int
