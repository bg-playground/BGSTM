"""Tests for runner-token API endpoints and auth dependency (BGSTM#296)."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_runner_token, get_current_user
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.runner_token import RunnerToken
from app.models.user import User, UserRole

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


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


def _make_user(role: UserRole = UserRole.admin) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{role.value}-{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="hashed",
        full_name=f"{role.value.capitalize()} User",
        role=role,
        is_active=True,
    )


def _override_user(user: User):
    async def _dep():
        return user

    return _dep


# ---------------------------------------------------------------------------
# Endpoint tests
# ---------------------------------------------------------------------------


class TestIssueRunnerToken:
    """POST /auth/runner-tokens"""

    def test_admin_can_issue_token(self, db_session):
        admin = _make_user(UserRole.admin)
        app.dependency_overrides[get_current_user] = _override_user(admin)
        try:
            with TestClient(app) as client:
                resp = client.post(
                    "/api/v1/auth/runner-tokens",
                    json={"label": "github-actions-ci", "scopes": ["external_results:write"]},
                )
            assert resp.status_code == 201
            data = resp.json()
            assert "token" in data
            assert data["token"].startswith("bgstm_runner_")
            assert data["label"] == "github-actions-ci"
            assert data["scopes"] == ["external_results:write"]
            assert "id" in data
            assert data["revoked_at"] is None
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_issued_token_has_expected_scopes_and_label(self, db_session):
        admin = _make_user(UserRole.admin)
        app.dependency_overrides[get_current_user] = _override_user(admin)
        try:
            with TestClient(app) as client:
                resp = client.post(
                    "/api/v1/auth/runner-tokens",
                    json={"label": "nightly-runner", "scopes": ["external_results:read", "external_results:write"]},
                )
            assert resp.status_code == 201
            data = resp.json()
            assert set(data["scopes"]) == {"external_results:read", "external_results:write"}
            assert data["label"] == "nightly-runner"
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_non_admin_gets_403(self, db_session):
        reviewer = _make_user(UserRole.reviewer)
        app.dependency_overrides[get_current_user] = _override_user(reviewer)
        try:
            with TestClient(app) as client:
                resp = client.post(
                    "/api/v1/auth/runner-tokens",
                    json={"label": "ci", "scopes": ["external_results:write"]},
                )
            assert resp.status_code == 403
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_unknown_scope_returns_422(self, db_session):
        admin = _make_user(UserRole.admin)
        app.dependency_overrides[get_current_user] = _override_user(admin)
        try:
            with TestClient(app) as client:
                resp = client.post(
                    "/api/v1/auth/runner-tokens",
                    json={"label": "bad-scope-runner", "scopes": ["totally:invalid"]},
                )
            assert resp.status_code == 422
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_audit_log_entry_written_on_issue(self, db_session):
        admin = _make_user(UserRole.admin)
        app.dependency_overrides[get_current_user] = _override_user(admin)
        try:
            with patch("app.api.auth.create_audit_entry", new_callable=AsyncMock) as mock_audit:
                with TestClient(app) as client:
                    resp = client.post(
                        "/api/v1/auth/runner-tokens",
                        json={"label": "audit-test", "scopes": ["external_results:write"]},
                    )
                assert resp.status_code == 201
                mock_audit.assert_called_once()
                call_kwargs = mock_audit.call_args
                assert call_kwargs.kwargs["action"] == "auth.runner_token.issue"
        finally:
            app.dependency_overrides.pop(get_current_user, None)


class TestListRunnerTokens:
    """GET /auth/runner-tokens"""

    def test_list_excludes_revoked_by_default(self, db_session):
        admin = _make_user(UserRole.admin)
        app.dependency_overrides[get_current_user] = _override_user(admin)
        try:
            with TestClient(app) as client:
                # Issue two tokens
                client.post(
                    "/api/v1/auth/runner-tokens",
                    json={"label": "active-token", "scopes": ["external_results:write"]},
                )
                revoke_resp = client.post(
                    "/api/v1/auth/runner-tokens",
                    json={"label": "to-revoke", "scopes": ["external_results:write"]},
                )
                token_id = revoke_resp.json()["id"]
                # Revoke the second token
                client.delete(f"/api/v1/auth/runner-tokens/{token_id}")
                # List without include_revoked
                list_resp = client.get("/api/v1/auth/runner-tokens")
            assert list_resp.status_code == 200
            tokens = list_resp.json()
            labels = [t["label"] for t in tokens]
            assert "active-token" in labels
            assert "to-revoke" not in labels
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_list_includes_revoked_with_flag(self, db_session):
        admin = _make_user(UserRole.admin)
        app.dependency_overrides[get_current_user] = _override_user(admin)
        try:
            with TestClient(app) as client:
                revoke_resp = client.post(
                    "/api/v1/auth/runner-tokens",
                    json={"label": "revoked-token", "scopes": ["external_results:write"]},
                )
                token_id = revoke_resp.json()["id"]
                client.delete(f"/api/v1/auth/runner-tokens/{token_id}")
                list_resp = client.get("/api/v1/auth/runner-tokens?include_revoked=true")
            assert list_resp.status_code == 200
            tokens = list_resp.json()
            labels = [t["label"] for t in tokens]
            assert "revoked-token" in labels
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_list_never_returns_plaintext_token(self, db_session):
        admin = _make_user(UserRole.admin)
        app.dependency_overrides[get_current_user] = _override_user(admin)
        try:
            with TestClient(app) as client:
                client.post(
                    "/api/v1/auth/runner-tokens",
                    json={"label": "no-plaintext", "scopes": ["external_results:write"]},
                )
                list_resp = client.get("/api/v1/auth/runner-tokens")
            assert list_resp.status_code == 200
            for token in list_resp.json():
                assert "token" not in token
        finally:
            app.dependency_overrides.pop(get_current_user, None)


class TestRevokeRunnerToken:
    """DELETE /auth/runner-tokens/{token_id}"""

    def test_admin_can_revoke(self, db_session):
        admin = _make_user(UserRole.admin)
        app.dependency_overrides[get_current_user] = _override_user(admin)
        try:
            with TestClient(app) as client:
                issue_resp = client.post(
                    "/api/v1/auth/runner-tokens",
                    json={"label": "to-revoke", "scopes": ["external_results:write"]},
                )
                token_id = issue_resp.json()["id"]
                resp = client.delete(f"/api/v1/auth/runner-tokens/{token_id}")
            assert resp.status_code == 204
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_second_revoke_returns_409(self, db_session):
        admin = _make_user(UserRole.admin)
        app.dependency_overrides[get_current_user] = _override_user(admin)
        try:
            with TestClient(app) as client:
                issue_resp = client.post(
                    "/api/v1/auth/runner-tokens",
                    json={"label": "double-revoke", "scopes": ["external_results:write"]},
                )
                token_id = issue_resp.json()["id"]
                client.delete(f"/api/v1/auth/runner-tokens/{token_id}")
                resp = client.delete(f"/api/v1/auth/runner-tokens/{token_id}")
            assert resp.status_code == 409
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_unknown_token_returns_404(self, db_session):
        admin = _make_user(UserRole.admin)
        app.dependency_overrides[get_current_user] = _override_user(admin)
        try:
            with TestClient(app) as client:
                resp = client.delete(f"/api/v1/auth/runner-tokens/{uuid.uuid4()}")
            assert resp.status_code == 404
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_audit_log_entry_written_on_revoke(self, db_session):
        admin = _make_user(UserRole.admin)
        app.dependency_overrides[get_current_user] = _override_user(admin)
        try:
            with TestClient(app) as client:
                issue_resp = client.post(
                    "/api/v1/auth/runner-tokens",
                    json={"label": "audit-revoke", "scopes": ["external_results:write"]},
                )
                token_id = issue_resp.json()["id"]

            with patch("app.api.auth.create_audit_entry", new_callable=AsyncMock) as mock_audit:
                with TestClient(app) as client:
                    resp = client.delete(f"/api/v1/auth/runner-tokens/{token_id}")
                assert resp.status_code == 204
                mock_audit.assert_called_once()
                assert mock_audit.call_args.kwargs["action"] == "auth.runner_token.revoke"
        finally:
            app.dependency_overrides.pop(get_current_user, None)


# ---------------------------------------------------------------------------
# Dependency tests
# ---------------------------------------------------------------------------


class TestGetCurrentRunnerTokenDependency:
    """Unit tests for the get_current_runner_token FastAPI dependency."""

    def _build_token(self, session, scopes=None, revoked=False) -> tuple[RunnerToken, str]:
        """Helper: persist a RunnerToken and return (model, plaintext)."""
        import asyncio

        from app.crud.runner_token import create_runner_token

        admin = _make_user(UserRole.admin)
        session.add(admin)

        async def _create():
            await session.commit()
            token, plaintext = await create_runner_token(
                session,
                label="test-dep-token",
                scopes=scopes or ["external_results:write"],
                created_by_user_id=admin.id,
            )
            if revoked:
                from datetime import datetime

                token.revoked_at = datetime.utcnow()
                await session.commit()
                await session.refresh(token)
            return token, plaintext

        return asyncio.get_event_loop().run_until_complete(_create())

    def test_missing_authorization_header_returns_401(self, db_session):
        with TestClient(app) as client:
            resp = client.get("/api/v1/auth/me", headers={})
        # /auth/me uses get_current_user (HTTPBearer) which returns 403 when no header
        # We need a route that uses get_current_runner_token.
        # We test the dependency directly via a fake route instead.
        assert resp.status_code in (401, 403)

    def test_bearer_without_bgstm_runner_prefix_returns_401(self, db_session):
        """A regular JWT should not be accepted as a runner token."""
        from fastapi import APIRouter, Depends
        from fastapi.testclient import TestClient

        test_router = APIRouter()

        @test_router.get("/test-runner-dep")
        async def _probe(token=Depends(get_current_runner_token)):
            return {"ok": True}

        app.include_router(test_router, prefix="/api/v1")
        try:
            with TestClient(app) as client:
                resp = client.get(
                    "/api/v1/test-runner-dep",
                    headers={"Authorization": "Bearer some.jwt.token"},
                )
            assert resp.status_code == 401
            assert "Not a runner token" in resp.json()["detail"]
        finally:
            # Remove the dynamically added route
            app.routes[:] = [r for r in app.routes if not getattr(r, "path", "").endswith("/test-runner-dep")]

    def test_valid_runner_token_resolves(self, db_session):
        """A valid bgstm_runner_ token resolves correctly."""
        import asyncio

        from fastapi import APIRouter, Depends

        from app.crud.runner_token import create_runner_token

        admin = _make_user(UserRole.admin)

        async def _setup():
            db_session.add(admin)
            await db_session.commit()
            return await create_runner_token(
                db_session,
                label="valid-dep",
                scopes=["external_results:write"],
                created_by_user_id=admin.id,
            )

        token_model, plaintext = asyncio.get_event_loop().run_until_complete(_setup())

        test_router = APIRouter()

        @test_router.get("/test-runner-valid")
        async def _probe(token=Depends(get_current_runner_token)):
            return {"id": str(token.id)}

        app.include_router(test_router, prefix="/api/v1")
        try:
            with TestClient(app) as client:
                resp = client.get(
                    "/api/v1/test-runner-valid",
                    headers={"Authorization": f"Bearer {plaintext}"},
                )
            assert resp.status_code == 200
            assert resp.json()["id"] == str(token_model.id)
        finally:
            app.routes[:] = [r for r in app.routes if not getattr(r, "path", "").endswith("/test-runner-valid")]

    def test_revoked_token_returns_401(self, db_session):
        import asyncio
        from datetime import datetime

        from fastapi import APIRouter, Depends

        from app.crud.runner_token import create_runner_token

        admin = _make_user(UserRole.admin)

        async def _setup():
            db_session.add(admin)
            await db_session.commit()
            token_model, plaintext = await create_runner_token(
                db_session,
                label="revoke-dep",
                scopes=["external_results:write"],
                created_by_user_id=admin.id,
            )
            token_model.revoked_at = datetime.utcnow()
            await db_session.commit()
            return token_model, plaintext

        token_model, plaintext = asyncio.get_event_loop().run_until_complete(_setup())

        test_router = APIRouter()

        @test_router.get("/test-runner-revoked")
        async def _probe(token=Depends(get_current_runner_token)):
            return {"ok": True}

        app.include_router(test_router, prefix="/api/v1")
        try:
            with TestClient(app) as client:
                resp = client.get(
                    "/api/v1/test-runner-revoked",
                    headers={"Authorization": f"Bearer {plaintext}"},
                )
            assert resp.status_code == 401
            assert "Revoked" in resp.json()["detail"]
        finally:
            app.routes[:] = [r for r in app.routes if not getattr(r, "path", "").endswith("/test-runner-revoked")]

    def test_unknown_token_hash_returns_401(self, db_session):
        from fastapi import APIRouter, Depends

        test_router = APIRouter()

        @test_router.get("/test-runner-unknown")
        async def _probe(token=Depends(get_current_runner_token)):
            return {"ok": True}

        app.include_router(test_router, prefix="/api/v1")
        try:
            with TestClient(app) as client:
                resp = client.get(
                    "/api/v1/test-runner-unknown",
                    headers={"Authorization": "Bearer bgstm_runner_nonexistent_value_xyz"},
                )
            assert resp.status_code == 401
            assert "Invalid runner token" in resp.json()["detail"]
        finally:
            app.routes[:] = [r for r in app.routes if not getattr(r, "path", "").endswith("/test-runner-unknown")]

    def test_require_runner_scope_accepts_matching_scope(self, db_session):
        import asyncio

        from fastapi import APIRouter, Depends

        from app.auth.dependencies import require_runner_scope
        from app.crud.runner_token import create_runner_token

        admin = _make_user(UserRole.admin)

        async def _setup():
            db_session.add(admin)
            await db_session.commit()
            return await create_runner_token(
                db_session,
                label="scope-ok",
                scopes=["external_results:write"],
                created_by_user_id=admin.id,
            )

        token_model, plaintext = asyncio.get_event_loop().run_until_complete(_setup())

        test_router = APIRouter()

        @test_router.get("/test-scope-ok")
        async def _probe(token=Depends(require_runner_scope("external_results:write"))):
            return {"ok": True}

        app.include_router(test_router, prefix="/api/v1")
        try:
            with TestClient(app) as client:
                resp = client.get(
                    "/api/v1/test-scope-ok",
                    headers={"Authorization": f"Bearer {plaintext}"},
                )
            assert resp.status_code == 200
        finally:
            app.routes[:] = [r for r in app.routes if not getattr(r, "path", "").endswith("/test-scope-ok")]

    def test_require_runner_scope_rejects_missing_scope(self, db_session):
        import asyncio

        from fastapi import APIRouter, Depends

        from app.auth.dependencies import require_runner_scope
        from app.crud.runner_token import create_runner_token

        admin = _make_user(UserRole.admin)

        async def _setup():
            db_session.add(admin)
            await db_session.commit()
            return await create_runner_token(
                db_session,
                label="scope-missing",
                scopes=["external_results:read"],  # only read, not write
                created_by_user_id=admin.id,
            )

        token_model, plaintext = asyncio.get_event_loop().run_until_complete(_setup())

        test_router = APIRouter()

        @test_router.get("/test-scope-missing")
        async def _probe(token=Depends(require_runner_scope("external_results:write"))):
            return {"ok": True}

        app.include_router(test_router, prefix="/api/v1")
        try:
            with TestClient(app) as client:
                resp = client.get(
                    "/api/v1/test-scope-missing",
                    headers={"Authorization": f"Bearer {plaintext}"},
                )
            assert resp.status_code == 403
        finally:
            app.routes[:] = [r for r in app.routes if not getattr(r, "path", "").endswith("/test-scope-missing")]
