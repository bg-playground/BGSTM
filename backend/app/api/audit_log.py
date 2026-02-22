"""API endpoint for Audit Log"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.crud.audit_log import get_audit_logs
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit_log import AuditLogListResponse

router = APIRouter()


@router.get("/audit-log", response_model=AuditLogListResponse)
async def list_audit_logs(
    user_id: UUID | None = Query(None, description="Filter by user ID"),
    action: str | None = Query(None, description="Filter by action (e.g. 'requirement.created')"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    date_from: datetime | None = Query(None, description="Filter entries on or after this datetime"),
    date_to: datetime | None = Query(None, description="Filter entries on or before this datetime"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List audit log entries (admin only)."""
    entries, total = await get_audit_logs(
        db,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
    return AuditLogListResponse(entries=entries, total=total)
