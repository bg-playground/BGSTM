"""API endpoints for Authentication"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user, require_admin
from app.auth.security import create_access_token, verify_password
from app.crud.audit_log import create_audit_entry
from app.crud.runner_token import (
    create_runner_token,
    get_runner_token_by_id,
    list_runner_tokens,
    revoke_runner_token,
)
from app.crud.user import create_user, get_user_by_email
from app.db.session import get_db
from app.models.user import User
from app.schemas.runner_token import RunnerTokenCreate, RunnerTokenIssueResponse, RunnerTokenResponse
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    existing = await get_user_by_email(db, user_create.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return await create_user(db, user_create)


@router.post("/auth/login", response_model=TokenResponse)
async def login(user_login: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate and return a JWT token"""
    user = await get_user_by_email(db, user_login.email)
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token)


@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user"""
    return current_user


# ---------------------------------------------------------------------------
# Runner-token endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/auth/runner-tokens",
    response_model=RunnerTokenIssueResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["auth"],
)
async def issue_runner_token(
    body: RunnerTokenCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Issue a new machine runner token (admin only).

    The plaintext token is returned **once** in the response and is never stored.
    Store it securely immediately after creation.
    """
    token, plaintext = await create_runner_token(
        db,
        label=body.label,
        scopes=body.scopes,
        created_by_user_id=current_user.id,
    )
    await create_audit_entry(
        db,
        user_id=current_user.id,
        action="auth.runner_token.issue",
        resource_type="runner_token",
        resource_id=str(token.id),
        details={"label": token.label, "scopes": token.scopes},
    )
    return RunnerTokenIssueResponse(
        id=token.id,
        label=token.label,
        scopes=token.scopes,
        created_at=token.created_at,
        last_used_at=token.last_used_at,
        revoked_at=token.revoked_at,
        token=plaintext,
    )


@router.get("/auth/runner-tokens", response_model=list[RunnerTokenResponse], tags=["auth"])
async def list_runner_tokens_endpoint(
    include_revoked: bool = Query(False, description="Include revoked tokens in the response"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all runner tokens (admin only).  Revoked tokens are hidden by default."""
    tokens = await list_runner_tokens(db, include_revoked=include_revoked)
    return tokens


@router.delete(
    "/auth/runner-tokens/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["auth"],
)
async def delete_runner_token(
    token_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Revoke a runner token (admin only).

    Returns 404 if the token does not exist and 409 if it is already revoked.
    """
    token = await get_runner_token_by_id(db, token_id)
    if token is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Runner token not found")
    if token.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Runner token already revoked")
    await revoke_runner_token(db, token_id)
    await create_audit_entry(
        db,
        user_id=current_user.id,
        action="auth.runner_token.revoke",
        resource_type="runner_token",
        resource_id=str(token.id),
        details={"label": token.label},
    )
