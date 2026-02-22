"""Tests for Audit Log functionality"""

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


REQ_PAYLOAD = {"title": "Audit Req", "description": "desc", "type": "functional", "priority": "high"}


@pytest.mark.asyncio
async def test_creating_requirement_creates_audit_log(db_session):
    """Creating a requirement should write an audit log entry."""
    admin = make_user(UserRole.admin)

    async def override():
        return admin

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as client:
        resp = client.post("/api/v1/requirements", json=REQ_PAYLOAD)
        assert resp.status_code == 201
        req_id = resp.json()["id"]

        logs_resp = client.get("/api/v1/audit-log")
    assert logs_resp.status_code == 200
    logs = logs_resp.json()
    assert len(logs) >= 1
    assert any(
        log["action"] == "create" and log["resource_type"] == "requirement" and log["resource_id"] == req_id
        for log in logs
    )


@pytest.mark.asyncio
async def test_admin_can_get_audit_log(db_session):
    """Admin can fetch the audit log."""
    admin = make_user(UserRole.admin)

    async def override():
        return admin

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as client:
        resp = client.get("/api/v1/audit-log")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_non_admin_cannot_get_audit_log(db_session):
    """Non-admin cannot access the audit log."""
    reviewer = make_user(UserRole.reviewer)

    async def override():
        return reviewer

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as client:
        resp = client.get("/api/v1/audit-log")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_audit_log_filter_by_action(db_session):
    """Audit log can be filtered by action."""
    admin = make_user(UserRole.admin)

    async def override():
        return admin

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as client:
        client.post("/api/v1/requirements", json=REQ_PAYLOAD)
        resp = client.get("/api/v1/audit-log?action=create")
    assert resp.status_code == 200
    logs = resp.json()
    assert all(log["action"] == "create" for log in logs)


@pytest.mark.asyncio
async def test_audit_log_filter_by_resource_type(db_session):
    """Audit log can be filtered by resource_type."""
    admin = make_user(UserRole.admin)

    async def override():
        return admin

    app.dependency_overrides[get_current_user] = override

    with TestClient(app) as client:
        client.post("/api/v1/requirements", json=REQ_PAYLOAD)
        resp = client.get("/api/v1/audit-log?resource_type=requirement")
    assert resp.status_code == 200
    logs = resp.json()
    assert all(log["resource_type"] == "requirement" for log in logs)
