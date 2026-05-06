"""Pydantic schemas for runner-token management (BGSTM#296)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

# Supported scope values for runner tokens.
VALID_SCOPES: frozenset[str] = frozenset(
    [
        "external_results:write",
        "external_results:read",
    ]
)


class RunnerTokenCreate(BaseModel):
    """Payload for ``POST /auth/runner-tokens``."""

    label: str
    scopes: list[str] = ["external_results:write"]

    @field_validator("scopes")
    @classmethod
    def validate_scopes(cls, v: list[str]) -> list[str]:
        unknown = set(v) - VALID_SCOPES
        if unknown:
            raise ValueError(f"Unknown scope(s): {sorted(unknown)}. Valid values: {sorted(VALID_SCOPES)}")
        if not v:
            raise ValueError("At least one scope is required.")
        return v


class RunnerTokenResponse(BaseModel):
    """Runner token metadata — plaintext is never included."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    label: str
    scopes: list[str]
    created_at: datetime
    last_used_at: datetime | None = None
    revoked_at: datetime | None = None


class RunnerTokenIssueResponse(RunnerTokenResponse):
    """Returned only at issuance — includes the plaintext token once."""

    token: str
