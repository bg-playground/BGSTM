"""Tests for JWT Authentication"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.crud.user import create_user, get_user_by_email
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.user import UserRole
from app.schemas.auth import UserCreate

# In-memory SQLite engine for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# --- CRUD tests (no fixtures needed, inline engine) ---


@pytest.mark.asyncio
async def test_create_user():
    """Test creating a user via CRUD"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        user = await create_user(session, UserCreate(email="test@example.com", password="secret123"))
        assert user.email == "test@example.com"
        assert user.hashed_password != "secret123"
        assert user.role == UserRole.VIEWER
        assert user.is_active is True

    await engine.dispose()


@pytest.mark.asyncio
async def test_get_user_by_email():
    """Test looking up a user by email"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        await create_user(session, UserCreate(email="lookup@example.com", password="pass"))
        user = await get_user_by_email(session, "lookup@example.com")
        assert user is not None
        assert user.email == "lookup@example.com"

        missing = await get_user_by_email(session, "nobody@example.com")
        assert missing is None

    await engine.dispose()


# --- API tests using TestClient ---


@pytest.mark.asyncio
async def test_register_success():
    """Test successful user registration"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            resp = client.post(
                "/api/v1/auth/register",
                json={"email": "newuser@example.com", "password": "password123", "full_name": "New User"},
            )
            assert resp.status_code == 201
            data = resp.json()
            assert data["email"] == "newuser@example.com"
            assert data["full_name"] == "New User"
            assert data["role"] == "viewer"
            assert data["is_active"] is True
            assert "id" in data
            assert "password" not in data
            assert "hashed_password" not in data
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Test that registering with duplicate email returns 400"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            payload = {"email": "dup@example.com", "password": "pass"}
            client.post("/api/v1/auth/register", json=payload)
            resp = client.post("/api/v1/auth/register", json=payload)
            assert resp.status_code == 400
            assert "already registered" in resp.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_login_success():
    """Test successful login returns JWT token"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            client.post("/api/v1/auth/register", json={"email": "login@example.com", "password": "mypassword"})
            resp = client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "mypassword"})
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_login_wrong_password():
    """Test login with wrong password returns 401"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            client.post("/api/v1/auth/register", json={"email": "wrongpw@example.com", "password": "correct"})
            resp = client.post("/api/v1/auth/login", json={"email": "wrongpw@example.com", "password": "wrong"})
            assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_login_nonexistent_user():
    """Test login with nonexistent user returns 401"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            resp = client.post("/api/v1/auth/login", json={"email": "ghost@example.com", "password": "pass"})
            assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_get_me_with_valid_token():
    """Test /auth/me returns user info with valid token"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            client.post("/api/v1/auth/register", json={"email": "me@example.com", "password": "mypass"})
            login_resp = client.post("/api/v1/auth/login", json={"email": "me@example.com", "password": "mypass"})
            token = login_resp.json()["access_token"]

            resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
            assert resp.status_code == 200
            data = resp.json()
            assert data["email"] == "me@example.com"
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    """Test that protected endpoints return 401 or 403 without token"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            resp = client.get("/api/v1/requirements")
            assert resp.status_code in (401, 403)
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token():
    """Test that protected endpoints return 401 with invalid token"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            resp = client.get("/api/v1/requirements", headers={"Authorization": "Bearer invalidtoken"})
            assert resp.status_code == 401
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token():
    """Test that protected endpoints work with valid token"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            client.post("/api/v1/auth/register", json={"email": "apiuser@example.com", "password": "apipass"})
            login_resp = client.post("/api/v1/auth/login", json={"email": "apiuser@example.com", "password": "apipass"})
            token = login_resp.json()["access_token"]

            resp = client.get("/api/v1/requirements", headers={"Authorization": f"Bearer {token}"})
            assert resp.status_code == 200
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()


@pytest.mark.asyncio
async def test_public_endpoints_accessible_without_token():
    """Test that public endpoints (root, health) are accessible without auth"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as client:
            assert client.get("/").status_code == 200
            assert client.get("/health").status_code == 200
    finally:
        app.dependency_overrides.clear()
        await engine.dispose()
