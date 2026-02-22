"""Tests for User Management API (admin only)"""

import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.auth.security import get_password_hash
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.user import User, UserRole


def make_admin() -> User:
    return User(
        id=uuid.uuid4(),
        email="admin@example.com",
        hashed_password="hashed",
        full_name="Admin User",
        role=UserRole.admin,
        is_active=True,
    )


@pytest_asyncio.fixture
async def admin_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    admin = make_admin()

    async with factory() as session:

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: admin
        yield session, admin
        app.dependency_overrides.clear()

    await engine.dispose()


async def _create_user_in_db(session: AsyncSession, email: str, role: UserRole = UserRole.reviewer) -> User:
    user = User(
        id=uuid.uuid4(),
        email=email,
        hashed_password=get_password_hash("pass"),
        full_name="Test User",
        role=role,
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# ── List users ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_users(admin_session):
    session, admin = admin_session
    await _create_user_in_db(session, "user1@example.com")
    await _create_user_in_db(session, "user2@example.com")

    with TestClient(app) as client:
        response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 2


# ── Get single user ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_user_by_id(admin_session):
    session, admin = admin_session
    user = await _create_user_in_db(session, "getme@example.com")

    with TestClient(app) as client:
        response = client.get(f"/api/v1/users/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "getme@example.com"


@pytest.mark.asyncio
async def test_get_nonexistent_user(admin_session):
    session, _ = admin_session
    with TestClient(app) as client:
        response = client.get(f"/api/v1/users/{uuid.uuid4()}")
    assert response.status_code == 404


# ── Update user ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_patch_user_role(admin_session):
    session, admin = admin_session
    user = await _create_user_in_db(session, "patch@example.com", UserRole.viewer)

    with TestClient(app) as client:
        response = client.patch(f"/api/v1/users/{user.id}", json={"role": "admin"})
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


@pytest.mark.asyncio
async def test_patch_user_deactivate(admin_session):
    session, admin = admin_session
    user = await _create_user_in_db(session, "deactivate@example.com")

    with TestClient(app) as client:
        response = client.patch(f"/api/v1/users/{user.id}", json={"is_active": False})
    assert response.status_code == 200
    assert response.json()["is_active"] is False


# ── Delete (deactivate) user ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_user(admin_session):
    session, admin = admin_session
    user = await _create_user_in_db(session, "delete@example.com")

    with TestClient(app) as client:
        response = client.delete(f"/api/v1/users/{user.id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_nonexistent_user(admin_session):
    session, _ = admin_session
    with TestClient(app) as client:
        response = client.delete(f"/api/v1/users/{uuid.uuid4()}")
    assert response.status_code == 404
