"""Tests for User Management API endpoints (admin only)"""

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


def make_user(role: UserRole) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{role.value}@example.com",
        hashed_password="hashed",
        full_name=f"{role.value} user",
        role=role,
        is_active=True,
    )


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


@pytest_asyncio.fixture
async def seeded_db(db_session):
    """Seed a few users into the DB for listing/getting."""
    users = [
        User(
            id=uuid.uuid4(),
            email="user1@example.com",
            hashed_password=get_password_hash("pass"),
            full_name="User One",
            role=UserRole.reviewer,
            is_active=True,
        ),
        User(
            id=uuid.uuid4(),
            email="user2@example.com",
            hashed_password=get_password_hash("pass"),
            full_name="User Two",
            role=UserRole.viewer,
            is_active=True,
        ),
    ]
    for u in users:
        db_session.add(u)
    await db_session.commit()
    return users


@pytest.mark.asyncio
async def test_admin_can_list_users(db_session, seeded_db):
    admin = make_user(UserRole.admin)

    async def override():
        return admin

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as client:
        resp = client.get("/api/v1/users")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


@pytest.mark.asyncio
async def test_non_admin_cannot_list_users(db_session):
    reviewer = make_user(UserRole.reviewer)

    async def override():
        return reviewer

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as client:
        resp = client.get("/api/v1/users")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_get_user_by_id(db_session, seeded_db):
    admin = make_user(UserRole.admin)

    async def override():
        return admin

    app.dependency_overrides[get_current_user] = override

    target_id = str(seeded_db[0].id)
    with TestClient(app) as client:
        resp = client.get(f"/api/v1/users/{target_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == target_id


@pytest.mark.asyncio
async def test_get_user_not_found(db_session):
    admin = make_user(UserRole.admin)

    async def override():
        return admin

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as client:
        resp = client.get(f"/api/v1/users/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_admin_can_update_user_role(db_session, seeded_db):
    admin = make_user(UserRole.admin)

    async def override():
        return admin

    app.dependency_overrides[get_current_user] = override

    target_id = str(seeded_db[0].id)
    with TestClient(app) as client:
        resp = client.patch(f"/api/v1/users/{target_id}", json={"role": "viewer"})
    assert resp.status_code == 200
    assert resp.json()["role"] == "viewer"


@pytest.mark.asyncio
async def test_admin_can_deactivate_user(db_session, seeded_db):
    admin = make_user(UserRole.admin)

    async def override():
        return admin

    app.dependency_overrides[get_current_user] = override

    target_id = str(seeded_db[1].id)
    with TestClient(app) as client:
        resp = client.delete(f"/api/v1/users/{target_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_cannot_self_deactivate(db_session):
    admin = make_user(UserRole.admin)
    # Add admin to DB so it can be found
    db_session.add(admin)
    await db_session.commit()

    async def override():
        return admin

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as client:
        resp = client.delete(f"/api/v1/users/{admin.id}")
    assert resp.status_code == 400
    assert "own account" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_non_admin_cannot_update_user(db_session, seeded_db):
    reviewer = make_user(UserRole.reviewer)

    async def override():
        return reviewer

    app.dependency_overrides[get_current_user] = override

    target_id = str(seeded_db[0].id)
    with TestClient(app) as client:
        resp = client.patch(f"/api/v1/users/{target_id}", json={"role": "admin"})
    assert resp.status_code == 403
