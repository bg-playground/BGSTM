"""API endpoints for Notifications"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.crud.notification import get_notifications, get_unread_count, mark_all_as_read, mark_as_read
from app.db.session import get_db
from app.models.user import User
from app.schemas.notification import NotificationListResponse, NotificationResponse

router = APIRouter()


@router.get("/notifications", response_model=NotificationListResponse)
async def list_notifications(
    unread_only: bool = Query(False, description="Return only unread notifications"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List the current user's notifications."""
    notifications, total = await get_notifications(
        db,
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    unread_count = await get_unread_count(db, user_id=current_user.id)
    return NotificationListResponse(
        notifications=notifications,
        unread_count=unread_count,
        total=total,
    )


@router.get("/notifications/unread-count", response_model=dict)
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get unread notification count for the current user."""
    count = await get_unread_count(db, user_id=current_user.id)
    return {"unread_count": count}


@router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a single notification as read."""
    notification = await mark_as_read(db, notification_id=notification_id, user_id=current_user.id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found",
        )
    return notification


@router.post("/notifications/mark-all-read", response_model=dict)
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark all notifications as read for the current user."""
    count = await mark_all_as_read(db, user_id=current_user.id)
    return {"marked_read": count}
