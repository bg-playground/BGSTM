from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.crud.runner_token import create_runner_token
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.project import Project
from app.models.user import User, UserRole


def _auth_header(plaintext: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {plaintext}"}


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
async def write_token(db_session):
    admin = User(
        id=uuid.uuid4(),
        email=f"admin-{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashed",
        full_name="Admin",
        role=UserRole.admin,
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()
    return await create_runner_token(
        db_session,
        label="write-token",
        scopes=["external_results:write"],
        created_by_user_id=admin.id,
    )


def _session_payload(project_id: str) -> dict:
    return {
        "runner": "pytest-bgstm@1.0.0",
        "project_id": project_id,
        "git_sha": "abc123",
        "git_branch": "main",
        "ci_url": f"https://ci.example.com/runs/{uuid.uuid4()}",
        "metadata": {},
    }


@pytest.mark.asyncio
async def test_create_session_unknown_project_returns_400(db_session, write_token):
    _model, plaintext = write_token

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/external-results/session",
            json=_session_payload(str(uuid.uuid4())),
            headers=_auth_header(plaintext),
        )

    assert response.status_code == 400, response.text
    detail = response.json()["detail"]
    assert detail["code"] == "session.project_not_found"


@pytest.mark.asyncio
async def test_create_session_valid_project_returns_201(db_session, write_token):
    project = Project(id=uuid.uuid4(), name="fk-project")
    db_session.add(project)
    await db_session.commit()

    _model, plaintext = write_token
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/external-results/session",
            json=_session_payload(str(project.id)),
            headers=_auth_header(plaintext),
        )

    assert response.status_code == 201, response.text
    assert response.json()["project_id"] == str(project.id)
