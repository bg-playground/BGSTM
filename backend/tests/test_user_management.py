"""Tests for User Management API endpoints"""

import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.crud.user import create_user
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.user import User, UserRole
from app.schemas.user import UserCreate

# ── Fixture ───────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with factory() as session:

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        yield session
        app.dependency_overrides.clear()

    await engine.dispose()


def _make_user_obj(role: UserRole, email: str | None = None) -> User:
    return User(
        id=uuid.uuid4(),
        email=email or f"{role.value}@example.com",
        hashed_password="hashed",
        full_name=f"{role.value.capitalize()} User",
        role=role,
        is_active=True,
    )


def _set_current_user(user: User):
    async def _dep():
        return user

    app.dependency_overrides[get_current_user] = _dep


def _clear_user():
    app.dependency_overrides.pop(get_current_user, None)


# ── List users ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_users_admin_only(db_session):
    """Admin can list all users."""
    admin = _make_user_obj(UserRole.admin)
    _set_current_user(admin)
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/users")
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total" in data
    finally:
        _clear_user()


@pytest.mark.asyncio
async def test_list_users_non_admin_forbidden(db_session):
    """Non-admin users get 403 on list users."""
    reviewer = _make_user_obj(UserRole.reviewer)
    _set_current_user(reviewer)
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/users")
        assert response.status_code == 403
    finally:
        _clear_user()


@pytest.mark.asyncio
async def test_list_users_viewer_forbidden(db_session):
    """Viewer users get 403 on list users."""
    viewer = _make_user_obj(UserRole.viewer)
    _set_current_user(viewer)
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/users")
        assert response.status_code == 403
    finally:
        _clear_user()


# ── Get user by ID ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_user_detail(db_session):
    """Admin can retrieve a specific user."""
    admin = _make_user_obj(UserRole.admin, email="admin_detail@example.com")
    db_session.add(admin)
    await db_session.commit()

    target = await create_user(
        db_session, UserCreate(email="target@example.com", password="pass", role=UserRole.viewer)
    )

    _set_current_user(admin)
    try:
        with TestClient(app) as client:
            response = client.get(f"/api/v1/users/{target.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "target@example.com"
        assert data["role"] == "viewer"
    finally:
        _clear_user()


@pytest.mark.asyncio
async def test_get_user_detail_not_found(db_session):
    """Returns 404 for non-existent user."""
    admin = _make_user_obj(UserRole.admin)
    _set_current_user(admin)
    try:
        with TestClient(app) as client:
            response = client.get(f"/api/v1/users/{uuid.uuid4()}")
        assert response.status_code == 404
    finally:
        _clear_user()


# ── Update user role ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_user_role(db_session):
    """Admin can update a user's role."""
    admin = _make_user_obj(UserRole.admin, email="admin_update@example.com")
    db_session.add(admin)
    await db_session.commit()

    target = await create_user(
        db_session, UserCreate(email="update_target@example.com", password="pass", role=UserRole.viewer)
    )

    _set_current_user(admin)
    try:
        with TestClient(app) as client:
            response = client.patch(f"/api/v1/users/{target.id}", json={"role": "reviewer"})
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "reviewer"
    finally:
        _clear_user()


@pytest.mark.asyncio
async def test_update_user_full_name(db_session):
    """Admin can update a user's full_name."""
    admin = _make_user_obj(UserRole.admin, email="admin_name@example.com")
    db_session.add(admin)
    await db_session.commit()

    target = await create_user(
        db_session, UserCreate(email="name_target@example.com", password="pass", full_name="Old Name")
    )

    _set_current_user(admin)
    try:
        with TestClient(app) as client:
            response = client.patch(f"/api/v1/users/{target.id}", json={"full_name": "New Name"})
        assert response.status_code == 200
        assert response.json()["full_name"] == "New Name"
    finally:
        _clear_user()


# ── Deactivate user ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_deactivate_user(db_session):
    """Admin can deactivate another user."""
    admin = _make_user_obj(UserRole.admin, email="admin_deact@example.com")
    db_session.add(admin)
    await db_session.commit()

    target = await create_user(
        db_session, UserCreate(email="deact_target@example.com", password="pass", role=UserRole.reviewer)
    )

    _set_current_user(admin)
    try:
        with TestClient(app) as client:
            response = client.delete(f"/api/v1/users/{target.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
    finally:
        _clear_user()


@pytest.mark.asyncio
async def test_cannot_deactivate_self(db_session):
    """Admin cannot deactivate their own account."""
    admin = _make_user_obj(UserRole.admin, email="admin_self@example.com")
    db_session.add(admin)
    await db_session.commit()

    _set_current_user(admin)
    try:
        with TestClient(app) as client:
            response = client.delete(f"/api/v1/users/{admin.id}")
        assert response.status_code == 400
        assert "self" in response.json()["detail"].lower() or "own" in response.json()["detail"].lower()
    finally:
        _clear_user()


@pytest.mark.asyncio
async def test_deactivate_nonexistent_user(db_session):
    """Returns 404 when trying to deactivate a non-existent user."""
    admin = _make_user_obj(UserRole.admin)
    _set_current_user(admin)
    try:
        with TestClient(app) as client:
            response = client.delete(f"/api/v1/users/{uuid.uuid4()}")
        assert response.status_code == 404
    finally:
        _clear_user()


@pytest.mark.asyncio
async def test_non_admin_cannot_deactivate(db_session):
    """Non-admin users cannot deactivate users."""
    reviewer = _make_user_obj(UserRole.reviewer)
    _set_current_user(reviewer)
    try:
        with TestClient(app) as client:
            response = client.delete(f"/api/v1/users/{uuid.uuid4()}")
        assert response.status_code == 403
    finally:
        _clear_user()
