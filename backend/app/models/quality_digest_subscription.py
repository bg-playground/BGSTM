"""Persisted Quality KPI digest preferences."""

import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.sql import func

from .base import Base
from .requirement import GUID, _enum_values


class DigestCadence(str, enum.Enum):
    off = "off"
    daily = "daily"
    weekly = "weekly"


class DigestChannel(str, enum.Enum):
    in_app = "in_app"


class QualityDigestSubscription(Base):
    __tablename__ = "quality_digest_subscriptions"
    __table_args__ = (UniqueConstraint("user_id", "channel", name="uq_quality_digest_user_channel"),)

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(Enum(DigestChannel, values_callable=_enum_values), nullable=False, default=DigestChannel.in_app)
    cadence = Column(Enum(DigestCadence, values_callable=_enum_values), nullable=False, default=DigestCadence.off)
    window_days = Column(Integer, nullable=False, default=30)
    last_delivered_at = Column(DateTime, nullable=True)
    next_delivery_at = Column(DateTime, nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
