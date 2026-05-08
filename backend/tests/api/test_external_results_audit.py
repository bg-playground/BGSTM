"""Integration tests for External Results audit wiring."""

from __future__ import annotations

import uuid
from types import SimpleNamespace

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.crud.audit_log import create_audit_entry
from app.crud.runner_token import create_runner_token
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.project import Project
from app.models.user import User, UserRole

_PROJECT_ID = str(uuid.uuid4())


def _make_user(role: UserRole = UserRole.admin) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{role.value}-{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashed",
        full_name=f"{role.value.capitalize()} User",
        role=role,
        is_active=True,
    )


def _auth_header(plaintext: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {plaintext}"}


def _session_payload() -> dict[str, str | dict[str, str]]:
    return {
        "runner": "pytest-bgstm@1.0.0",
        "project_id": _PROJECT_ID,
        "git_sha": "abc123",
        "git_branch": "main",
        "ci_url": f"https://ci.example.com/runs/{uuid.uuid4()}",
        "metadata": {"os": "ubuntu-22.04"},
    }


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        project = Project(id=uuid.UUID(_PROJECT_ID), name=f"project-{uuid.uuid4().hex[:6]}")
        session.add(project)
        await session.commit()

        async def _override_get_db():
            yield session

        app.dependency_overrides[get_db] = _override_get_db
        yield session
        app.dependency_overrides.clear()

    await engine.dispose()


@pytest_asyncio.fixture
async def admin_user(db_session):
    admin = _make_user(UserRole.admin)
    db_session.add(admin)
    await db_session.commit()
    return admin


@pytest_asyncio.fixture
async def write_token(db_session, admin_user):
    return await create_runner_token(
        db_session,
        label="write-token",
        scopes=["external_results:write"],
        created_by_user_id=admin_user.id,
    )


def test_session_start_writes_audit(monkeypatch, db_session, write_token):
    captured: list[dict] = []

    async def fake_write_audit(db, **kwargs):
        captured.append(kwargs)
        return SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr("app.api.external_results.write_audit", fake_write_audit)

    token_model, plaintext = write_token
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/external-results/session",
            json=_session_payload(),
            headers=_auth_header(plaintext),
        )

    assert response.status_code == 201, response.text
    assert any(c["action"] == "external_results.session.start" for c in captured)
    assert captured[0]["actor_kind"] == "runner_token"
    assert captured[0]["actor_id"] == token_model.id


def test_session_finish_writes_audit(monkeypatch, db_session, write_token):
    captured: list[dict] = []

    async def fake_write_audit(db, **kwargs):
        captured.append(kwargs)
        return SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr("app.api.external_results.write_audit", fake_write_audit)

    _token_model, plaintext = write_token
    with TestClient(app) as client:
        create_resp = client.post(
            "/api/v1/external-results/session",
            json=_session_payload(),
            headers=_auth_header(plaintext),
        )
        assert create_resp.status_code == 201, create_resp.text
        session_id = create_resp.json()["id"]
        finish_resp = client.patch(
            f"/api/v1/external-results/session/{session_id}",
            json={"status": "passed", "summary": {"total": 1, "passed": 1}},
            headers=_auth_header(plaintext),
        )

    assert finish_resp.status_code == 200, finish_resp.text
    assert any(c["action"] == "external_results.session.finish" for c in captured)


def test_session_start_idempotent_calls_still_write_audit(monkeypatch, db_session, write_token):
    captured: list[dict] = []

    async def fake_write_audit(db, **kwargs):
        captured.append(kwargs)
        return SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr("app.api.external_results.write_audit", fake_write_audit)

    _token_model, plaintext = write_token
    payload = _session_payload()
    with TestClient(app) as client:
        first = client.post("/api/v1/external-results/session", json=payload, headers=_auth_header(plaintext))
        second = client.post("/api/v1/external-results/session", json=payload, headers=_auth_header(plaintext))

    assert first.status_code == 201
    assert second.status_code == 201
    assert len([c for c in captured if c["action"] == "external_results.session.start"]) == 2


@pytest.mark.asyncio
async def test_audit_log_filter_runner_token_returns_external_results_entries(db_session, admin_user, write_token):
    _token_model, plaintext = write_token
    with TestClient(app) as client:
        create_resp = client.post(
            "/api/v1/external-results/session",
            json=_session_payload(),
            headers=_auth_header(plaintext),
        )
        assert create_resp.status_code == 201, create_resp.text

        async def override_admin():
            return admin_user

        app.dependency_overrides[get_current_user] = override_admin
        try:
            response = client.get("/api/v1/audit-log?actor_kind=runner_token")
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(entry["action"] == "external_results.session.start" for entry in data["entries"])


@pytest.mark.asyncio
async def test_audit_log_filter_user_still_returns_user_entries(db_session, admin_user):
    await create_audit_entry(
        db_session,
        user_id=admin_user.id,
        action="requirement.created",
        resource_type="requirement",
        resource_id=str(uuid.uuid4()),
    )

    async def override_admin():
        return admin_user

    app.dependency_overrides[get_current_user] = override_admin
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/audit-log?actor_kind=user")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(entry["actor_kind"] == "user" for entry in data["entries"])
