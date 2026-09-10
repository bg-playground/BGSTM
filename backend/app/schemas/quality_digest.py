"""Schemas for Quality KPI digest subscriptions."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.quality_digest_subscription import DigestCadence, DigestChannel


class DigestSubscriptionUpdate(BaseModel):
    cadence: DigestCadence
    window_days: Literal[7, 30, 90] = 30
    channel: DigestChannel = DigestChannel.in_app


class DigestSubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    channel: DigestChannel
    cadence: DigestCadence
    window_days: Literal[7, 30, 90]
    last_delivered_at: datetime | None
    next_delivery_at: datetime | None
    created_at: datetime
    updated_at: datetime
