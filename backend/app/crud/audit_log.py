"""CRUD operations for AuditLog"""

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def create_audit_entry(
    db: AsyncSession,
    user_id: UUID | str | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    """Create a new audit log entry"""
    entry = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


def _build_audit_filter(
    user_id: UUID | str | None,
    action: str | None,
    resource_type: str | None,
):
    """Build WHERE conditions for audit log queries."""
    conditions = []
    if user_id is not None:
        conditions.append(AuditLog.user_id == user_id)
    if action is not None:
        conditions.append(AuditLog.action == action)
    if resource_type is not None:
        conditions.append(AuditLog.resource_type == resource_type)
    return conditions


async def count_audit_logs(
    db: AsyncSession,
    user_id: UUID | str | None = None,
    action: str | None = None,
    resource_type: str | None = None,
) -> int:
    """Count audit log entries matching optional filters"""
    conditions = _build_audit_filter(user_id, action, resource_type)
    query = select(func.count()).select_from(AuditLog)
    for cond in conditions:
        query = query.where(cond)
    result = await db.execute(query)
    return result.scalar_one()


async def get_audit_logs(
    db: AsyncSession,
    user_id: UUID | str | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[AuditLog]:
    """Get audit log entries with optional filters and pagination"""
    conditions = _build_audit_filter(user_id, action, resource_type)
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    for cond in conditions:
        query = query.where(cond)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())
