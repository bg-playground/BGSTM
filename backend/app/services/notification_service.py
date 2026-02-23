"""Notification service helpers — create notifications on domain events."""

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.notification import create_notification, create_notification_for_all_users
from app.models.notification import NotificationType
from app.models.user import UserRole

logger = logging.getLogger(__name__)


async def notify_suggestions_generated(
    db: AsyncSession,
    user_id: UUID,
    suggestions_created: int,
    pairs_analyzed: int,
) -> None:
    """Called after suggestion generation completes — notifies the requesting user."""
    try:
        await create_notification(
            db,
            user_id=user_id,
            type=NotificationType.SUGGESTIONS_GENERATED,
            title="Suggestions Generated",
            message=(
                f"AI suggestion generation completed: {suggestions_created} suggestions created"
                f" from {pairs_analyzed} pairs analyzed."
            ),
            metadata={"suggestions_created": suggestions_created, "pairs_analyzed": pairs_analyzed},
        )
    except Exception:
        logger.exception("Failed to create suggestions_generated notification")


async def notify_coverage_drop(
    db: AsyncSession,
    previous_coverage: float,
    current_coverage: float,
    threshold: float = 80.0,
) -> None:
    """Called when coverage drops below threshold — notifies all admins."""
    if current_coverage >= threshold:
        return
    try:
        from sqlalchemy import select

        from app.models.user import User

        result = await db.execute(
            select(User).where(User.role == UserRole.admin, User.is_active.is_(True))  # type: ignore[attr-defined]
        )
        admins = result.scalars().all()
        for admin in admins:
            await create_notification(
                db,
                user_id=admin.id,
                type=NotificationType.COVERAGE_DROP,
                title="Coverage Drop Alert",
                message=(
                    f"Test coverage dropped from {previous_coverage:.1f}% to {current_coverage:.1f}%,"
                    f" below the {threshold:.1f}% threshold."
                ),
                metadata={
                    "previous_coverage": previous_coverage,
                    "current_coverage": current_coverage,
                    "threshold": threshold,
                },
            )
    except Exception:
        logger.exception("Failed to create coverage_drop notification")


async def notify_suggestion_reviewed(
    db: AsyncSession,
    reviewer_user_id: UUID,
    suggestion_count: int,
    status: str,
) -> None:
    """Called after suggestion review/bulk review — notifies the reviewer."""
    try:
        label = "suggestion" if suggestion_count == 1 else "suggestions"
        await create_notification(
            db,
            user_id=reviewer_user_id,
            type=NotificationType.SUGGESTION_REVIEWED,
            title="Suggestion Review Complete",
            message=f"{suggestion_count} {label} marked as {status}.",
            metadata={"suggestion_count": suggestion_count, "status": status},
        )
    except Exception:
        logger.exception("Failed to create suggestion_reviewed notification")


async def notify_requirement_created(
    db: AsyncSession,
    creator_user_id: UUID,
    requirement_title: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Called after requirement creation — notifies all users except creator."""
    try:
        await create_notification_for_all_users(
            db,
            type=NotificationType.REQUIREMENT_CREATED,
            title="New Requirement Created",
            message=f'A new requirement was created: "{requirement_title}".',
            metadata=metadata,
            exclude_user_id=creator_user_id,
        )
    except Exception:
        logger.exception("Failed to create requirement_created notification")


async def notify_test_case_created(
    db: AsyncSession,
    creator_user_id: UUID,
    test_case_title: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Called after test case creation — notifies all users except creator."""
    try:
        await create_notification_for_all_users(
            db,
            type=NotificationType.TEST_CASE_CREATED,
            title="New Test Case Created",
            message=f'A new test case was created: "{test_case_title}".',
            metadata=metadata,
            exclude_user_id=creator_user_id,
        )
    except Exception:
        logger.exception("Failed to create test_case_created notification")
