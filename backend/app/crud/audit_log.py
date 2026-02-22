"""CRUD operations for Audit Log"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


async def create_audit_entry(
    db: AsyncSession,
    user_id: UUID,
    action: str,
    resource_type: str,
    resource_id: str,
    details: dict | None = None,
) -> AuditLog:
    """Create a new audit log entry."""
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


async def get_audit_logs(
    db: AsyncSession,
    user_id: UUID | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[AuditLog], int]:
    """Get audit logs with optional filters. Returns (entries, total_count)."""
    query = select(AuditLog)

    if user_id is not None:
        query = query.where(AuditLog.user_id == user_id)
    if action is not None:
        query = query.where(AuditLog.action == action)
    if resource_type is not None:
        query = query.where(AuditLog.resource_type == resource_type)
    if date_from is not None:
        query = query.where(AuditLog.created_at >= date_from)
    if date_to is not None:
        query = query.where(AuditLog.created_at <= date_to)

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar_one()

    query = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all()), total
