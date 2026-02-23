"""CRUD operations for Notifications"""

from typing import Any
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification, NotificationType
from app.models.user import User


async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    type: NotificationType,
    title: str,
    message: str,
    metadata: dict[str, Any] | None = None,
) -> Notification:
    """Create a single notification for a user."""
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        metadata_=metadata,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def create_notification_for_all_users(
    db: AsyncSession,
    type: NotificationType,
    title: str,
    message: str,
    metadata: dict[str, Any] | None = None,
    exclude_user_id: UUID | None = None,
) -> list[Notification]:
    """Create a notification for all active users, optionally excluding one."""
    query = select(User).where(User.is_active.is_(True))  # type: ignore[attr-defined]
    if exclude_user_id is not None:
        query = query.where(User.id != exclude_user_id)
    result = await db.execute(query)
    users = result.scalars().all()

    notifications = [
        Notification(
            user_id=u.id,
            type=type,
            title=title,
            message=message,
            metadata_=metadata,
        )
        for u in users
    ]
    db.add_all(notifications)
    await db.commit()
    return notifications


async def get_notifications(
    db: AsyncSession,
    user_id: UUID,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Notification], int]:
    """Get notifications for a user. Returns (notifications, total)."""
    query = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        query = query.where(Notification.read.is_(False))  # type: ignore[attr-defined]

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    query = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_unread_count(db: AsyncSession, user_id: UUID) -> int:
    """Get unread notification count for a user."""
    result = await db.execute(
        select(func.count()).where(Notification.user_id == user_id, Notification.read.is_(False))  # type: ignore[attr-defined]
    )
    return result.scalar_one()


async def mark_as_read(db: AsyncSession, notification_id: UUID, user_id: UUID) -> Notification | None:
    """Mark a single notification as read. Returns None if not found or not owned by user."""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
    )
    notification = result.scalar_one_or_none()
    if notification is None:
        return None
    notification.read = True
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_all_as_read(db: AsyncSession, user_id: UUID) -> int:
    """Mark all notifications as read for a user. Returns number of updated rows."""
    result = await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.read.is_(False))  # type: ignore[attr-defined]
        .values(read=True)
    )
    await db.commit()
    return result.rowcount
