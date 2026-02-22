"""CRUD operations for Users"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get a user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user(db: AsyncSession, user_id: str | UUID) -> User | None:
    """Get a user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
    """Create a new user, hashing the password before storing"""
    hashed_password = get_password_hash(user_create.password)
    db_user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        full_name=user_create.full_name,
        role=user_create.role,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    """Get all users with pagination"""
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def get_users_count(db: AsyncSession) -> int:
    """Count all users"""
    result = await db.execute(select(func.count()).select_from(User))
    return result.scalar_one()


async def update_user(db: AsyncSession, user_id: str | UUID, user_update: UserUpdate) -> User | None:
    """Update a user's fields"""
    user = await get_user(db, user_id)
    if not user:
        return None
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(db: AsyncSession, user_id: str | UUID) -> User | None:
    """Deactivate (soft-delete) a user"""
    user = await get_user(db, user_id)
    if not user:
        return None
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user
