"""CRUD helpers for Quality KPI digest subscriptions."""

from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.quality_digest_subscription import DigestCadence, DigestChannel, QualityDigestSubscription
from app.models.user import User


def next_delivery(cadence: DigestCadence, now: datetime) -> datetime | None:
    if cadence == DigestCadence.off:
        return None
    delta = timedelta(days=1 if cadence == DigestCadence.daily else 7)
    return now + delta


async def get_subscription(
    db: AsyncSession,
    user_id: UUID,
    channel: DigestChannel = DigestChannel.in_app,
) -> QualityDigestSubscription | None:
    result = await db.execute(
        select(QualityDigestSubscription).where(
            QualityDigestSubscription.user_id == user_id,
            QualityDigestSubscription.channel == channel,
        )
    )
    return result.scalar_one_or_none()


async def upsert_subscription(
    db: AsyncSession,
    user_id: UUID,
    cadence: DigestCadence,
    window_days: int,
    channel: DigestChannel = DigestChannel.in_app,
    now: datetime | None = None,
) -> QualityDigestSubscription:
    now = now or datetime.utcnow()
    subscription = await get_subscription(db, user_id, channel)
    if subscription is None:
        subscription = QualityDigestSubscription(user_id=user_id, channel=channel)
        db.add(subscription)
    subscription.cadence = cadence
    subscription.window_days = window_days
    subscription.next_delivery_at = next_delivery(cadence, now)
    await db.commit()
    await db.refresh(subscription)
    return subscription


async def get_due_subscriptions(db: AsyncSession, now: datetime) -> list[QualityDigestSubscription]:
    result = await db.execute(
        select(QualityDigestSubscription)
        .join(User, User.id == QualityDigestSubscription.user_id)
        .where(
            User.is_active.is_(True),
            QualityDigestSubscription.cadence != DigestCadence.off,
            QualityDigestSubscription.next_delivery_at.is_not(None),
            QualityDigestSubscription.next_delivery_at <= now,
        )
        .order_by(QualityDigestSubscription.next_delivery_at.asc())
    )
    return list(result.scalars().all())


async def mark_delivered(
    db: AsyncSession,
    subscription: QualityDigestSubscription,
    delivered_at: datetime,
) -> None:
    subscription.last_delivered_at = delivered_at
    subscription.next_delivery_at = next_delivery(subscription.cadence, delivered_at)
    await db.commit()
