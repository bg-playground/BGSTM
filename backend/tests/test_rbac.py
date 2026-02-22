"""Tests for RBAC role enforcement"""

import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.user import User, UserRole


def make_user(role: UserRole) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{role.value}@example.com",
        hashed_password="hashed",
        full_name=f"{role.value.title()} User",
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


def set_user(role: UserRole) -> User:
    user = make_user(role)
    app.dependency_overrides[get_current_user] = lambda: user
    return user


# ── Requirements RBAC ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_viewer_cannot_create_requirement(db_session):
    set_user(UserRole.viewer)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/requirements",
            json={"title": "Req", "description": "desc", "type": "functional", "priority": "medium"},
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_can_create_requirement(db_session):
    set_user(UserRole.reviewer)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/requirements",
            json={"title": "Req", "description": "desc", "type": "functional", "priority": "medium"},
        )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_admin_can_create_requirement(db_session):
    set_user(UserRole.admin)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/requirements",
            json={"title": "Req", "description": "desc", "type": "functional", "priority": "medium"},
        )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_viewer_can_list_requirements(db_session):
    set_user(UserRole.viewer)
    with TestClient(app) as client:
        response = client.get("/api/v1/requirements")
    assert response.status_code == 200


# ── Test Cases RBAC ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_viewer_cannot_create_test_case(db_session):
    set_user(UserRole.viewer)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/test-cases",
            json={"title": "TC", "description": "desc", "type": "functional", "priority": "medium"},
        )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_can_create_test_case(db_session):
    set_user(UserRole.reviewer)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/test-cases",
            json={"title": "TC", "description": "desc", "type": "functional", "priority": "medium"},
        )
    assert response.status_code == 201


# ── Suggestions generate RBAC ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reviewer_cannot_generate_suggestions(db_session):
    set_user(UserRole.reviewer)
    with TestClient(app) as client:
        response = client.post("/api/v1/suggestions/generate")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_viewer_cannot_generate_suggestions(db_session):
    set_user(UserRole.viewer)
    with TestClient(app) as client:
        response = client.post("/api/v1/suggestions/generate")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_generate_suggestions(db_session):
    set_user(UserRole.admin)
    with TestClient(app) as client:
        response = client.post("/api/v1/suggestions/generate?algorithm=keyword")
    # Should succeed (empty DB just returns 0 suggestions)
    assert response.status_code == 200


# ── User management RBAC ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_viewer_cannot_list_users(db_session):
    set_user(UserRole.viewer)
    with TestClient(app) as client:
        response = client.get("/api/v1/users")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_cannot_list_users(db_session):
    set_user(UserRole.reviewer)
    with TestClient(app) as client:
        response = client.get("/api/v1/users")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_users(db_session):
    set_user(UserRole.admin)
    with TestClient(app) as client:
        response = client.get("/api/v1/users")
    assert response.status_code == 200


# ── Audit log RBAC ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_viewer_cannot_access_audit_log(db_session):
    set_user(UserRole.viewer)
    with TestClient(app) as client:
        response = client.get("/api/v1/audit-log")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_cannot_access_audit_log(db_session):
    set_user(UserRole.reviewer)
    with TestClient(app) as client:
        response = client.get("/api/v1/audit-log")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_audit_log(db_session):
    set_user(UserRole.admin)
    with TestClient(app) as client:
        response = client.get("/api/v1/audit-log")
    assert response.status_code == 200
