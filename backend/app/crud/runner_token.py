"""CRUD operations for RunnerToken (BGSTM#296)."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import generate_runner_token, generate_token_salt, hash_runner_token
from app.models.runner_token import RunnerToken


async def create_runner_token(
    db: AsyncSession,
    *,
    label: str,
    scopes: list[str],
    created_by_user_id: UUID,
) -> tuple[RunnerToken, str]:
    """Create a new runner token.

    Returns ``(RunnerToken model, plaintext_token)``.  The plaintext is returned
    **once** and is never persisted; callers must surface it to the admin immediately.
    """
    plaintext = generate_runner_token()
    salt = generate_token_salt()
    hashed = hash_runner_token(plaintext, salt)

    token = RunnerToken(
        hashed_token=hashed,
        salt=salt,
        label=label,
        scopes=scopes,
        created_by_user_id=created_by_user_id,
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token, plaintext


async def get_runner_token_by_hash(db: AsyncSession, hashed: str) -> RunnerToken | None:
    """Look up a runner token by its hashed value."""
    result = await db.execute(select(RunnerToken).where(RunnerToken.hashed_token == hashed))
    return result.scalar_one_or_none()


async def get_runner_token_by_id(db: AsyncSession, token_id: UUID) -> RunnerToken | None:
    """Look up a runner token by its primary key."""
    result = await db.execute(select(RunnerToken).where(RunnerToken.id == token_id))
    return result.scalar_one_or_none()


async def list_runner_tokens(
    db: AsyncSession,
    *,
    include_revoked: bool = False,
) -> list[RunnerToken]:
    """Return all runner tokens, optionally filtering out revoked ones."""
    query = select(RunnerToken)
    if not include_revoked:
        query = query.where(RunnerToken.revoked_at.is_(None))
    query = query.order_by(RunnerToken.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def revoke_runner_token(db: AsyncSession, token_id: UUID) -> RunnerToken:
    """Set ``revoked_at`` on the token.  Caller must verify the token exists first."""
    token = await get_runner_token_by_id(db, token_id)
    if token is None:
        raise ValueError(f"RunnerToken {token_id} not found")
    token.revoked_at = datetime.utcnow()
    await db.commit()
    await db.refresh(token)
    return token


async def update_last_used(db: AsyncSession, token: RunnerToken) -> None:
    """Stamp ``last_used_at`` without refreshing the full object."""
    token.last_used_at = datetime.utcnow()
    await db.commit()
