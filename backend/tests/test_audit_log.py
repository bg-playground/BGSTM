"""Tests for AuditLog CRUD and API"""

import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.crud.audit_log import create_audit_entry, get_audit_logs
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.user import User, UserRole


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


# ── CRUD tests ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_audit_entry(db_session):
    """Test creating an audit log entry"""
    user_id = uuid.uuid4()
    entry = await create_audit_entry(db_session, user_id, "create", "requirement", "req-123")
    assert entry.id is not None
    assert entry.user_id == user_id
    assert entry.action == "create"
    assert entry.resource_type == "requirement"
    assert entry.resource_id == "req-123"
    assert entry.details is None


@pytest.mark.asyncio
async def test_create_audit_entry_with_details(db_session):
    """Test creating an audit log entry with details"""
    user_id = uuid.uuid4()
    entry = await create_audit_entry(db_session, user_id, "generate_suggestions", "suggestion", None, {"count": 5})
    assert entry.details == {"count": 5}


@pytest.mark.asyncio
async def test_get_audit_logs_no_filter(db_session):
    """Test retrieving audit logs without filters"""
    user_id = uuid.uuid4()
    await create_audit_entry(db_session, user_id, "create", "requirement", "req-1")
    await create_audit_entry(db_session, user_id, "delete", "test_case", "tc-1")

    logs = await get_audit_logs(db_session)
    assert len(logs) == 2


@pytest.mark.asyncio
async def test_get_audit_logs_filter_by_action(db_session):
    """Test filtering audit logs by action"""
    user_id = uuid.uuid4()
    await create_audit_entry(db_session, user_id, "create", "requirement", "req-1")
    await create_audit_entry(db_session, user_id, "delete", "requirement", "req-2")

    logs = await get_audit_logs(db_session, action="create")
    assert len(logs) == 1
    assert logs[0].action == "create"


@pytest.mark.asyncio
async def test_get_audit_logs_filter_by_resource_type(db_session):
    """Test filtering audit logs by resource_type"""
    user_id = uuid.uuid4()
    await create_audit_entry(db_session, user_id, "create", "requirement", "req-1")
    await create_audit_entry(db_session, user_id, "create", "test_case", "tc-1")

    logs = await get_audit_logs(db_session, resource_type="test_case")
    assert len(logs) == 1
    assert logs[0].resource_type == "test_case"


@pytest.mark.asyncio
async def test_get_audit_logs_pagination(db_session):
    """Test audit log pagination"""
    user_id = uuid.uuid4()
    for i in range(5):
        await create_audit_entry(db_session, user_id, "create", "requirement", f"req-{i}")

    logs = await get_audit_logs(db_session, skip=2, limit=2)
    assert len(logs) == 2


# ── API tests ─────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def admin_db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    admin_user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        hashed_password="hashed",
        full_name="Admin User",
        role=UserRole.admin,
        is_active=True,
    )

    async with factory() as session:

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = lambda: admin_user
        yield session
        app.dependency_overrides.clear()

    await engine.dispose()


@pytest.mark.asyncio
async def test_audit_log_api_returns_entries(admin_db_session):
    """Test audit log API returns entries"""
    user_id = uuid.uuid4()
    await create_audit_entry(admin_db_session, user_id, "create", "requirement", "req-1")

    with TestClient(app) as client:
        response = client.get("/api/v1/audit-log")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_audit_log_api_filter_by_action(admin_db_session):
    """Test audit log API filtering by action"""
    user_id = uuid.uuid4()
    await create_audit_entry(admin_db_session, user_id, "create", "requirement", "req-1")
    await create_audit_entry(admin_db_session, user_id, "delete", "requirement", "req-2")

    with TestClient(app) as client:
        response = client.get("/api/v1/audit-log?action=create")
    assert response.status_code == 200
    data = response.json()
    assert all(item["action"] == "create" for item in data["items"])


@pytest.mark.asyncio
async def test_audit_log_api_filter_by_resource_type(admin_db_session):
    """Test audit log API filtering by resource_type"""
    user_id = uuid.uuid4()
    await create_audit_entry(admin_db_session, user_id, "create", "requirement", "req-1")
    await create_audit_entry(admin_db_session, user_id, "create", "test_case", "tc-1")

    with TestClient(app) as client:
        response = client.get("/api/v1/audit-log?resource_type=test_case")
    assert response.status_code == 200
    data = response.json()
    assert all(item["resource_type"] == "test_case" for item in data["items"])
