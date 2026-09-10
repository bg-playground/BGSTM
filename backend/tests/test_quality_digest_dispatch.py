from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import Base
from app.models.notification import Notification
from app.models.quality_digest_delivery import QualityDigestDelivery
from app.models.quality_digest_subscription import DigestCadence, DigestChannel, QualityDigestSubscription
from app.models.user import User
from app.services import quality_digest_service as service
from app.services.quality_digest_service import QualityDigest


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


async def _subscription(db: AsyncSession, *, active: bool = True) -> tuple[User, QualityDigestSubscription, datetime]:
    due_at = datetime(2026, 9, 10, 12, 0, 0)
    user = User(
        email=f"digest-{active}@example.com",
        hashed_password="not-used",
        is_active=active,
    )
    db.add(user)
    await db.flush()
    subscription = QualityDigestSubscription(
        user_id=user.id,
        channel=DigestChannel.in_app,
        cadence=DigestCadence.daily,
        window_days=30,
        next_delivery_at=due_at,
    )
    db.add(subscription)
    await db.commit()
    return user, subscription, due_at


def _digest() -> QualityDigest:
    return QualityDigest(
        window_days=30,
        title="Quality KPI Digest — 30 days",
        body="No execution data is available yet.",
        dashboard_path="/quality-dashboard?window=30",
    )


@pytest.mark.asyncio
async def test_due_period_is_delivered_once_and_immediate_rerun_is_noop(db_session, monkeypatch) -> None:
    _, subscription, due_at = await _subscription(db_session)

    async def fake_build_digest(db, window_days):
        return _digest()

    monkeypatch.setattr(service, "build_digest", fake_build_digest)
    now = due_at + timedelta(minutes=5)

    assert await service.dispatch_due_digests(db_session, now) == 1
    assert await service.dispatch_due_digests(db_session, now) == 0

    notification_count = await db_session.scalar(select(func.count()).select_from(Notification))
    delivery_count = await db_session.scalar(select(func.count()).select_from(QualityDigestDelivery))
    await db_session.refresh(subscription)

    assert notification_count == 1
    assert delivery_count == 1
    assert subscription.last_delivered_at == now
    assert subscription.next_delivery_at == now + timedelta(days=1)


@pytest.mark.asyncio
async def test_failed_delivery_rolls_back_claim_notification_and_schedule(db_session, monkeypatch) -> None:
    _, subscription, due_at = await _subscription(db_session)

    async def fail_build_digest(db, window_days):
        raise RuntimeError("synthetic digest failure")

    monkeypatch.setattr(service, "build_digest", fail_build_digest)

    with pytest.raises(RuntimeError, match="synthetic digest failure"):
        await service.dispatch_due_digests(db_session, due_at + timedelta(minutes=5))

    notification_count = await db_session.scalar(select(func.count()).select_from(Notification))
    delivery_count = await db_session.scalar(select(func.count()).select_from(QualityDigestDelivery))
    stored = await db_session.get(QualityDigestSubscription, subscription.id)

    assert notification_count == 0
    assert delivery_count == 0
    assert stored is not None
    assert stored.last_delivered_at is None
    assert stored.next_delivery_at == due_at


@pytest.mark.asyncio
async def test_inactive_user_subscription_is_not_dispatched(db_session, monkeypatch) -> None:
    await _subscription(db_session, active=False)

    async def fail_if_called(db, window_days):
        raise AssertionError("inactive subscription should not build a digest")

    monkeypatch.setattr(service, "build_digest", fail_if_called)

    delivered = await service.dispatch_due_digests(db_session, datetime(2026, 9, 10, 12, 5, 0))
    assert delivered == 0
    assert await db_session.scalar(select(func.count()).select_from(Notification)) == 0
    assert await db_session.scalar(select(func.count()).select_from(QualityDigestDelivery)) == 0
