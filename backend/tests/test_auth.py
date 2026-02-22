"""Tests for Auth API endpoints"""

import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.session import get_db
from app.main import app
from app.models.base import Base

# ── Fixture ───────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture
async def db_session():
    """Provide an in-memory SQLite session and override the FastAPI dependency."""
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


# ── Registration tests ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_register_success(db_session):
    """Test successful user registration"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword",
                "full_name": "New User",
                "role": "reviewer",
            },
        )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert data["role"] == "reviewer"
    assert data["is_active"] is True
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(db_session):
    """Test registration with a duplicate email returns 400"""
    with TestClient(app) as client:
        client.post(
            "/api/v1/auth/register",
            json={"email": "dup@example.com", "password": "pass1"},
        )
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "dup@example.com", "password": "pass2"},
        )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_default_role(db_session):
    """Test that the default role is 'reviewer'"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "default@example.com", "password": "pass"},
        )
    assert response.status_code == 201
    assert response.json()["role"] == "reviewer"


# ── Login tests ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_success(db_session):
    """Test successful login returns a JWT token"""
    with TestClient(app) as client:
        client.post(
            "/api/v1/auth/register",
            json={"email": "login@example.com", "password": "mypassword"},
        )
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "login@example.com", "password": "mypassword"},
        )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(db_session):
    """Test login with wrong password returns 401"""
    with TestClient(app) as client:
        client.post(
            "/api/v1/auth/register",
            json={"email": "wrongpw@example.com", "password": "correctpass"},
        )
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "wrongpw@example.com", "password": "wrongpass"},
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(db_session):
    """Test login for non-existent user returns 401"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "pass"},
        )
    assert response.status_code == 401


# ── /auth/me tests ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_me_with_valid_token(db_session):
    """Test /auth/me with a valid token returns the current user"""
    with TestClient(app) as client:
        client.post(
            "/api/v1/auth/register",
            json={"email": "me@example.com", "password": "pass", "full_name": "Me User"},
        )
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "me@example.com", "password": "pass"},
        )
        token = login_resp.json()["access_token"]
        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["full_name"] == "Me User"


@pytest.mark.asyncio
async def test_get_me_without_token(db_session):
    """Test /auth/me without a token returns 403 (no credentials)"""
    with TestClient(app) as client:
        response = client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_me_with_expired_token(db_session):
    """Test /auth/me with an expired token returns 401"""
    with TestClient(app) as client:
        client.post(
            "/api/v1/auth/register",
            json={"email": "expired@example.com", "password": "pass"},
        )
        # Create an already-expired token
        expired_payload = {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


# ── Protected endpoint tests ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(db_session):
    """Test a protected endpoint is accessible with a valid token"""
    with TestClient(app) as client:
        client.post(
            "/api/v1/auth/register",
            json={"email": "protected@example.com", "password": "pass"},
        )
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "protected@example.com", "password": "pass"},
        )
        token = login_resp.json()["access_token"]
        response = client.get("/api/v1/requirements", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(db_session):
    """Test a protected endpoint is inaccessible without a token"""
    with TestClient(app) as client:
        response = client.get("/api/v1/requirements")
    assert response.status_code in (401, 403)
