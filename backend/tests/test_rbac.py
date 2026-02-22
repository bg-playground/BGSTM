"""Tests for RBAC (Role-Based Access Control)"""

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


def set_user_role(role: UserRole):
    user = make_user(role)

    async def override_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_get_current_user
    return user


REQ_PAYLOAD = {"title": "RBAC Req", "description": "desc", "type": "functional", "priority": "high"}
TC_PAYLOAD = {"title": "RBAC TC", "description": "desc", "type": "functional", "priority": "high"}


# ── Requirements RBAC ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_viewer_can_get_requirements(db_session):
    set_user_role(UserRole.viewer)
    with TestClient(app) as client:
        resp = client.get("/api/v1/requirements")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_viewer_cannot_post_requirement(db_session):
    set_user_role(UserRole.viewer)
    with TestClient(app) as client:
        resp = client.post("/api/v1/requirements", json=REQ_PAYLOAD)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_can_post_requirement(db_session):
    set_user_role(UserRole.reviewer)
    with TestClient(app) as client:
        resp = client.post("/api/v1/requirements", json=REQ_PAYLOAD)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_admin_can_post_requirement(db_session):
    set_user_role(UserRole.admin)
    with TestClient(app) as client:
        resp = client.post("/api/v1/requirements", json=REQ_PAYLOAD)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_viewer_cannot_delete_requirement(db_session):
    set_user_role(UserRole.reviewer)
    with TestClient(app) as client:
        create_resp = client.post("/api/v1/requirements", json=REQ_PAYLOAD)
        req_id = create_resp.json()["id"]

    set_user_role(UserRole.viewer)
    with TestClient(app) as client:
        resp = client.delete(f"/api/v1/requirements/{req_id}")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_can_delete_requirement(db_session):
    set_user_role(UserRole.reviewer)
    with TestClient(app) as client:
        create_resp = client.post("/api/v1/requirements", json=REQ_PAYLOAD)
        req_id = create_resp.json()["id"]
        resp = client.delete(f"/api/v1/requirements/{req_id}")
    assert resp.status_code == 204


# ── Test Cases RBAC ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_viewer_cannot_post_test_case(db_session):
    set_user_role(UserRole.viewer)
    with TestClient(app) as client:
        resp = client.post("/api/v1/test-cases", json=TC_PAYLOAD)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_can_post_test_case(db_session):
    set_user_role(UserRole.reviewer)
    with TestClient(app) as client:
        resp = client.post("/api/v1/test-cases", json=TC_PAYLOAD)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_viewer_can_get_test_cases(db_session):
    set_user_role(UserRole.viewer)
    with TestClient(app) as client:
        resp = client.get("/api/v1/test-cases")
    assert resp.status_code == 200


# ── Admin-only endpoints RBAC ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_viewer_cannot_access_users_endpoint(db_session):
    set_user_role(UserRole.viewer)
    with TestClient(app) as client:
        resp = client.get("/api/v1/users")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_cannot_access_users_endpoint(db_session):
    set_user_role(UserRole.reviewer)
    with TestClient(app) as client:
        resp = client.get("/api/v1/users")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_users_endpoint(db_session):
    set_user_role(UserRole.admin)
    with TestClient(app) as client:
        resp = client.get("/api/v1/users")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_viewer_cannot_access_audit_log(db_session):
    set_user_role(UserRole.viewer)
    with TestClient(app) as client:
        resp = client.get("/api/v1/audit-log")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_reviewer_cannot_access_audit_log(db_session):
    set_user_role(UserRole.reviewer)
    with TestClient(app) as client:
        resp = client.get("/api/v1/audit-log")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_audit_log(db_session):
    set_user_role(UserRole.admin)
    with TestClient(app) as client:
        resp = client.get("/api/v1/audit-log")
    assert resp.status_code == 200
