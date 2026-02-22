"""API endpoints for Audit Logs"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.crud import audit_log as crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse

router = APIRouter()


@router.get("/audit-log", response_model=list[AuditLogResponse])
async def list_audit_logs(
    user_id: UUID | None = Query(None),
    action: str | None = Query(None),
    resource_type: str | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await crud.get_audit_logs(
        db,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )
