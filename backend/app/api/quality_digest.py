"""Authenticated Quality KPI digest subscription endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.crud.quality_digest import get_subscription, upsert_subscription
from app.db.session import get_db
from app.models.quality_digest_subscription import DigestCadence, DigestChannel
from app.models.user import User
from app.schemas.quality_digest import DigestSubscriptionResponse, DigestSubscriptionUpdate

router = APIRouter(prefix="/quality-digest")


@router.get("/subscription", response_model=DigestSubscriptionResponse | None)
async def read_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_subscription(db, current_user.id)


@router.put("/subscription", response_model=DigestSubscriptionResponse)
async def write_subscription(
    payload: DigestSubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await upsert_subscription(
        db,
        current_user.id,
        payload.cadence,
        payload.window_days,
        payload.channel,
        datetime.utcnow(),
    )


@router.delete("/subscription", response_model=DigestSubscriptionResponse)
async def disable_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await upsert_subscription(
        db,
        current_user.id,
        DigestCadence.off,
        30,
        DigestChannel.in_app,
        datetime.utcnow(),
    )
