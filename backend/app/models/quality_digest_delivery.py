"""Durable delivery ledger for scheduled Quality KPI digests."""

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from .base import Base
from .requirement import GUID


class QualityDigestDelivery(Base):
    __tablename__ = "quality_digest_deliveries"
    __table_args__ = (
        UniqueConstraint(
            "subscription_id",
            "due_at",
            name="uq_quality_digest_delivery_subscription_due",
        ),
    )

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(
        GUID(),
        ForeignKey("quality_digest_subscriptions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    due_at = Column(DateTime, nullable=False)
    delivered_at = Column(DateTime, nullable=False)
    notification_id = Column(GUID(), ForeignKey("notifications.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
