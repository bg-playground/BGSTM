"""Tests for Audit Log functionality"""

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


def _make_admin() -> User:
    return User(
        id=uuid.uuid4(),
        email="admin@example.com",
        hashed_password="hashed",
        full_name="Admin",
        role=UserRole.admin,
        is_active=True,
    )


def _make_reviewer() -> User:
    return User(
        id=uuid.uuid4(),
        email="reviewer@example.com",
        hashed_password="hashed",
        full_name="Reviewer",
        role=UserRole.reviewer,
        is_active=True,
    )


# ── CRUD tests ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_audit_entry(db_session):
    """Creating an audit entry persists to the database."""
    admin = _make_admin()
    db_session.add(admin)
    await db_session.commit()

    entry = await create_audit_entry(
        db_session,
        user_id=admin.id,
        action="requirement.created",
        resource_type="requirement",
        resource_id=str(uuid.uuid4()),
        details={"title": "My Req"},
    )

    assert entry.id is not None
    assert entry.action == "requirement.created"
    assert entry.resource_type == "requirement"
    assert entry.details == {"title": "My Req"}


@pytest.mark.asyncio
async def test_get_audit_logs_no_filter(db_session):
    """get_audit_logs returns all entries when no filter is applied."""
    admin = _make_admin()
    db_session.add(admin)
    await db_session.commit()

    for action in ("requirement.created", "requirement.updated", "link.deleted"):
        await create_audit_entry(
            db_session,
            user_id=admin.id,
            action=action,
            resource_type="requirement",
            resource_id=str(uuid.uuid4()),
        )

    entries, total = await get_audit_logs(db_session)
    assert total == 3
    assert len(entries) == 3


@pytest.mark.asyncio
async def test_get_audit_logs_filter_by_action(db_session):
    """get_audit_logs filters by action correctly."""
    admin = _make_admin()
    db_session.add(admin)
    await db_session.commit()

    await create_audit_entry(
        db_session, user_id=admin.id, action="requirement.created", resource_type="requirement", resource_id="1"
    )
    await create_audit_entry(db_session, user_id=admin.id, action="link.deleted", resource_type="link", resource_id="2")

    entries, total = await get_audit_logs(db_session, action="requirement.created")
    assert total == 1
    assert entries[0].action == "requirement.created"


@pytest.mark.asyncio
async def test_get_audit_logs_filter_by_resource_type(db_session):
    """get_audit_logs filters by resource_type."""
    admin = _make_admin()
    db_session.add(admin)
    await db_session.commit()

    await create_audit_entry(
        db_session, user_id=admin.id, action="requirement.created", resource_type="requirement", resource_id="1"
    )
    await create_audit_entry(db_session, user_id=admin.id, action="link.deleted", resource_type="link", resource_id="2")

    entries, total = await get_audit_logs(db_session, resource_type="link")
    assert total == 1
    assert entries[0].resource_type == "link"


# ── API endpoint tests ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_audit_log_endpoint_admin_access(db_session):
    """Admin can access the audit log endpoint."""
    admin = _make_admin()
    db_session.add(admin)
    await db_session.commit()

    async def override_admin():
        return admin

    app.dependency_overrides[get_current_user] = override_admin
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/audit-log")
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        assert "total" in data
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_audit_log_endpoint_non_admin_forbidden(db_session):
    """Non-admin users get 403 on the audit log endpoint."""
    reviewer = _make_reviewer()

    async def override_reviewer():
        return reviewer

    app.dependency_overrides[get_current_user] = override_reviewer
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/audit-log")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_creating_requirement_generates_audit_entry(db_session):
    """Creating a requirement via the API produces an audit log entry."""
    admin = _make_admin()
    db_session.add(admin)
    await db_session.commit()

    async def override_admin():
        return admin

    app.dependency_overrides[get_current_user] = override_admin
    try:
        with TestClient(app) as client:
            client.post(
                "/api/v1/requirements",
                json={
                    "title": "Audited Req",
                    "description": "For audit test",
                    "type": "functional",
                    "priority": "medium",
                },
            )

            # Check audit entry was created
            response = client.get("/api/v1/audit-log?action=requirement.created")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert any(e["action"] == "requirement.created" for e in data["entries"])
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_audit_log_endpoint_with_filters(db_session):
    """Audit log endpoint supports filtering by action and resource_type."""
    admin = _make_admin()
    db_session.add(admin)
    await db_session.commit()

    # Insert some entries directly
    for action, rtype in [("requirement.created", "requirement"), ("link.deleted", "link")]:
        await create_audit_entry(db_session, user_id=admin.id, action=action, resource_type=rtype, resource_id="x")

    async def override_admin():
        return admin

    app.dependency_overrides[get_current_user] = override_admin
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/audit-log?resource_type=link")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["entries"][0]["resource_type"] == "link"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
