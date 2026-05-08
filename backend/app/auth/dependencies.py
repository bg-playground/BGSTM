from collections.abc import Callable
from typing import Any

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_access_token, hash_runner_token
from app.db.session import get_db
from app.models.runner_token import RunnerToken
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    from app.crud.user import get_user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await get_user(db, user_id)
    if user is None or not user.is_active:
        raise credentials_exception

    return user


async def require_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Require an active authenticated user (is_active already checked in get_current_user)."""
    return current_user


async def require_reviewer_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require reviewer or admin role."""
    if current_user.role not in (UserRole.reviewer, UserRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer or admin role required",
        )
    return current_user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role."""
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user


# ---------------------------------------------------------------------------
# Runner-token dependencies
# ---------------------------------------------------------------------------

_RUNNER_TOKEN_PREFIX = "bgstm_runner_"


async def get_current_runner_token(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> RunnerToken:
    """Resolve ``Authorization: Bearer bgstm_runner_<...>`` to a RunnerToken.

    Raises 401 if the header is missing/malformed, the token is unknown, or it
    has been revoked.  Updates ``last_used_at`` on every successful resolution.
    """
    from app.crud.runner_token import update_last_used

    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    # Parse "Bearer <value>"
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    raw_token = parts[1]
    if not raw_token.startswith(_RUNNER_TOKEN_PREFIX):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not a runner token")

    # We need the salt to re-derive the hash, so we must look up by prefix scan.
    # The stored hash was derived as SHA-256(salt + plaintext).  Because we only
    # store the hash (not the plaintext), we cannot do a single-step lookup.
    # Instead we perform a linear scan over *active* tokens — acceptable given the
    # small expected cardinality of runner tokens.
    from sqlalchemy import select

    from app.models.runner_token import RunnerToken as RT

    result = await db.execute(select(RT))
    all_tokens = list(result.scalars().all())

    matched: RunnerToken | None = None
    for candidate in all_tokens:
        if hash_runner_token(raw_token, candidate.salt) == candidate.hashed_token:
            matched = candidate
            break

    if matched is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid runner token")

    if matched.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Revoked runner token")

    await update_last_used(db, matched)
    return matched


def require_runner_scope(scope: str) -> Callable[..., Any]:
    """Return a FastAPI dependency that requires *scope* on the resolved runner token.

    Usage::

        @router.post(..., dependencies=[Depends(require_runner_scope("external_results:write"))])
    """

    async def _dependency(token: RunnerToken = Depends(get_current_runner_token)) -> RunnerToken:
        if scope not in (token.scopes or []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Runner token does not have the required scope: {scope!r}",
            )
        return token

    return _dependency


async def get_runner_or_user_auth(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> RunnerToken | User:
    """Accept either a runner token or a user JWT for read access."""
    if authorization and authorization.lower().startswith("bearer bgstm_runner_"):
        try:
            return await get_current_runner_token(authorization=authorization, db=db)
        except HTTPException:
            pass

    if authorization and authorization.lower().startswith("bearer "):
        raw_token = authorization.split(" ", 1)[1]
        payload = decode_access_token(raw_token)
        if payload is not None:
            user_id = payload.get("sub")
            if user_id:
                from app.crud.user import get_user

                user = await get_user(db, user_id)
                if user and user.is_active:
                    return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "auth.invalid", "message": "Missing or invalid credentials.", "details": None},
    )
