from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.main import app
from app.models.audit_log import AuditLog
from app.models.base import Base
from app.models.project import Project
from app.models.user import User, UserRole


def _make_user(role: UserRole) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{role.value}-{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashed",
        full_name=f"{role.value.capitalize()} User",
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

        async def _override_get_db():
            yield session

        app.dependency_overrides[get_db] = _override_get_db
        yield session
        app.dependency_overrides.clear()

    await engine.dispose()


@pytest_asyncio.fixture
async def users(db_session):
    admin = _make_user(UserRole.admin)
    reviewer = _make_user(UserRole.reviewer)
    viewer = _make_user(UserRole.viewer)
    db_session.add_all([admin, reviewer, viewer])
    await db_session.commit()
    return {"admin": admin, "reviewer": reviewer, "viewer": viewer}


def _set_current_user(user: User) -> None:
    async def _override_user():
        return user

    app.dependency_overrides[get_current_user] = _override_user


def _clear_current_user() -> None:
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("role", "expected_status"),
    [("admin", 201), ("reviewer", 201), ("viewer", 403)],
)
async def test_create_project_auth_and_audit(db_session, users, role: str, expected_status: int):
    _set_current_user(users[role])
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/projects", json={"name": "Project A", "description": "Created in test"})
    finally:
        _clear_current_user()

    assert response.status_code == expected_status, response.text

    if expected_status == 201:
        data = response.json()
        assert data["name"] == "Project A"
        assert data["description"] == "Created in test"

        created = await db_session.execute(select(Project).where(Project.id == uuid.UUID(data["id"])))
        assert created.scalar_one().name == "Project A"

        audit_result = await db_session.execute(
            select(AuditLog).where(AuditLog.action == "project.create").order_by(AuditLog.created_at.desc())
        )
        audit = audit_result.scalar_one()
        assert audit.actor_kind == "user"
        assert audit.user_id == users[role].id
        assert audit.actor_token_id is None
        assert audit.resource_type == "project"
        assert audit.resource_id == data["id"]
        assert audit.details == {"name": "Project A", "description": "Created in test"}


@pytest.mark.asyncio
async def test_create_project_unauthenticated(db_session):
    with TestClient(app) as client:
        response = client.post("/api/v1/projects", json={"name": "Project A"})
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ["admin", "reviewer", "viewer"])
async def test_list_and_get_projects_any_authenticated_role(db_session, users, role: str):
    project = Project(id=uuid.uuid4(), name="Project B", description="Existing")
    db_session.add(project)
    await db_session.commit()

    _set_current_user(users[role])
    try:
        with TestClient(app) as client:
            list_response = client.get("/api/v1/projects")
            get_response = client.get(f"/api/v1/projects/{project.id}")
            missing_response = client.get(f"/api/v1/projects/{uuid.uuid4()}")
    finally:
        _clear_current_user()

    assert list_response.status_code == 200, list_response.text
    list_data = list_response.json()
    assert list_data["total"] >= 1
    assert list_data["page"] == 1
    assert isinstance(list_data["items"], list)
    assert any(item["id"] == str(project.id) for item in list_data["items"])

    assert get_response.status_code == 200, get_response.text
    assert get_response.json()["id"] == str(project.id)
    assert missing_response.status_code == 404


@pytest.mark.asyncio
async def test_list_projects_unauthenticated(db_session):
    with TestClient(app) as client:
        response = client.get("/api/v1/projects")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("role", "expected_status"),
    [("admin", 200), ("reviewer", 200), ("viewer", 403)],
)
async def test_patch_project_auth_and_audit(db_session, users, role: str, expected_status: int):
    project = Project(id=uuid.uuid4(), name="Before Name", description="Before Desc")
    db_session.add(project)
    await db_session.commit()

    _set_current_user(users[role])
    try:
        with TestClient(app) as client:
            response = client.patch(
                f"/api/v1/projects/{project.id}",
                json={"name": "After Name", "description": "After Desc"},
            )
    finally:
        _clear_current_user()

    assert response.status_code == expected_status, response.text

    if expected_status == 200:
        data = response.json()
        assert data["name"] == "After Name"
        assert data["description"] == "After Desc"

        audit_result = await db_session.execute(
            select(AuditLog).where(AuditLog.action == "project.update").order_by(AuditLog.created_at.desc())
        )
        audit = audit_result.scalar_one()
        assert audit.actor_kind == "user"
        assert audit.user_id == users[role].id
        assert audit.actor_token_id is None
        assert audit.resource_type == "project"
        assert audit.resource_id == str(project.id)
        assert audit.details == {
            "name": {"from": "Before Name", "to": "After Name"},
            "description": {"from": "Before Desc", "to": "After Desc"},
        }


@pytest.mark.asyncio
async def test_patch_project_not_found(db_session, users):
    _set_current_user(users["admin"])
    try:
        with TestClient(app) as client:
            response = client.patch(f"/api/v1/projects/{uuid.uuid4()}", json={"name": "Nope"})
    finally:
        _clear_current_user()

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_project_unauthenticated(db_session):
    with TestClient(app) as client:
        response = client.patch(f"/api/v1/projects/{uuid.uuid4()}", json={"name": "No Auth"})
    assert response.status_code in (401, 403)
