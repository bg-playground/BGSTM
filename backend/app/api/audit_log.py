"""API endpoints for Audit Log"""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.crud.audit_log import count_audit_logs, get_audit_logs
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit_log import AuditLogListResponse

router = APIRouter()


@router.get("/audit-log", response_model=AuditLogListResponse)
async def list_audit_logs(
    user_id: UUID | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List audit log entries (admin only)"""
    total = await count_audit_logs(db, user_id=user_id, action=action, resource_type=resource_type)
    items = await get_audit_logs(
        db, user_id=user_id, action=action, resource_type=resource_type, skip=skip, limit=limit
    )
    return AuditLogListResponse(items=items, total=total, skip=skip, limit=limit)
