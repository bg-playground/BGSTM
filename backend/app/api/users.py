"""API endpoints for User Management (admin only)"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_admin
from app.crud.user import deactivate_user, get_user, get_users, get_users_count, update_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserListResponse, UserResponse, UserUpdate

router = APIRouter()


@router.get("/users", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all users (admin only)"""
    total = await get_users_count(db)
    users = await get_users(db, skip=skip, limit=limit)
    return UserListResponse(items=users, total=total, skip=skip, limit=limit)


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get a specific user by ID (admin only)"""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
async def patch_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a user's role or status (admin only)"""
    user = await update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Deactivate a user (admin only)"""
    user = await deactivate_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found")
