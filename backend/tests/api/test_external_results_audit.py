"""Integration tests for External Results audit wiring."""

from __future__ import annotations

import io
import uuid
from types import SimpleNamespace

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.external_results import router as external_results_router
from app.auth.dependencies import get_current_user
from app.crud.audit_log import create_audit_entry
from app.crud.runner_token import create_runner_token
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.project import Project
from app.models.user import User, UserRole
from app.storage.base import StorageResult

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


# ---------------------------------------------------------------------------
# Per-endpoint audit-emission tests
# ---------------------------------------------------------------------------


def test_case_create_writes_audit(monkeypatch, db_session, write_token):
    captured: list[dict] = []

    async def fake_write_audit(db, **kwargs):
        captured.append(kwargs)
        return SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr("app.api.external_results.write_audit", fake_write_audit)

    token_model, plaintext = write_token
    with TestClient(app) as client:
        session_resp = client.post(
            "/api/v1/external-results/session",
            json=_session_payload(),
            headers=_auth_header(plaintext),
        )
        assert session_resp.status_code == 201, session_resp.text
        session_id = session_resp.json()["id"]

        resp = client.post(
            "/api/v1/external-results/case",
            json={
                "session_id": session_id,
                "external_id": f"TC-{uuid.uuid4()}",
                "title": "Audit test case",
                "outcome": "passed",
                "duration_ms": 50,
                "requirement_ids": [],
                "requirement_external_ids": ["REQ-001"],
            },
            headers=_auth_header(plaintext),
        )

    assert resp.status_code == 201, resp.text
    create_audit = next((c for c in captured if c["action"] == "external_results.case.create"), None)
    assert create_audit is not None
    assert create_audit["actor_kind"] == "runner_token"
    assert create_audit["actor_id"] == token_model.id
    details = create_audit["details"]
    assert "session_id" in details
    assert "outcome" in details
    assert "external_id" in details
    assert "auto_registered" in details


def test_case_create_idempotent_writes_separate_audit(monkeypatch, db_session, write_token):
    captured: list[dict] = []

    async def fake_write_audit(db, **kwargs):
        captured.append(kwargs)
        return SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr("app.api.external_results.write_audit", fake_write_audit)

    _token_model, plaintext = write_token
    with TestClient(app) as client:
        session_resp = client.post(
            "/api/v1/external-results/session",
            json=_session_payload(),
            headers=_auth_header(plaintext),
        )
        assert session_resp.status_code == 201, session_resp.text
        session_id = session_resp.json()["id"]

        case_payload = {
            "session_id": session_id,
            "external_id": f"TC-idem-{uuid.uuid4()}",
            "title": "Idempotent test case",
            "outcome": "passed",
            "duration_ms": 30,
            "requirement_ids": [],
        }
        first = client.post("/api/v1/external-results/case", json=case_payload, headers=_auth_header(plaintext))
        second = client.post("/api/v1/external-results/case", json=case_payload, headers=_auth_header(plaintext))

    assert first.status_code == 201, first.text
    assert second.status_code == 200, second.text
    create_audits = [c for c in captured if c["action"] == "external_results.case.create"]
    idempotent_audits = [c for c in captured if c["action"] == "external_results.case.create.idempotent"]
    assert len(create_audits) == 1
    assert len(idempotent_audits) == 1


def test_case_update_writes_audit(monkeypatch, db_session, write_token):
    captured: list[dict] = []

    async def fake_write_audit(db, **kwargs):
        captured.append(kwargs)
        return SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr("app.api.external_results.write_audit", fake_write_audit)

    _token_model, plaintext = write_token
    with TestClient(app) as client:
        session_resp = client.post(
            "/api/v1/external-results/session",
            json=_session_payload(),
            headers=_auth_header(plaintext),
        )
        assert session_resp.status_code == 201, session_resp.text
        session_id = session_resp.json()["id"]

        create_resp = client.post(
            "/api/v1/external-results/case",
            json={
                "session_id": session_id,
                "external_id": f"TC-upd-{uuid.uuid4()}",
                "title": "Update test case",
                "outcome": "passed",
                "duration_ms": 30,
                "requirement_ids": [],
            },
            headers=_auth_header(plaintext),
        )
        assert create_resp.status_code == 201, create_resp.text
        case_id = create_resp.json()["id"]

        patch_resp = client.patch(
            f"/api/v1/external-results/case/{case_id}",
            json={"outcome": "flaky"},
            headers=_auth_header(plaintext),
        )

    assert patch_resp.status_code == 200, patch_resp.text
    update_audit = next((c for c in captured if c["action"] == "external_results.case.update"), None)
    assert update_audit is not None
    details = update_audit["details"]
    assert "previous_outcome" in details
    assert "new_outcome" in details
    assert details["previous_outcome"] == "passed"
    assert details["new_outcome"] == "flaky"


def test_artifact_upload_writes_audit(monkeypatch, db_session, write_token):
    captured: list[dict] = []

    async def fake_write_audit(db, **kwargs):
        captured.append(kwargs)
        return SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr("app.api.external_results.write_audit", fake_write_audit)

    fake_storage_result = StorageResult(
        key="test/artifact/test.png",
        url="http://example.com/test.png",
        size_bytes=72,
        content_type="image/png",
    )
    monkeypatch.setattr(
        "app.api.external_results.get_storage",
        lambda: SimpleNamespace(save=lambda stream, *, key, content_type: fake_storage_result),
    )

    _token_model, plaintext = write_token
    with TestClient(app) as client:
        session_resp = client.post(
            "/api/v1/external-results/session",
            json=_session_payload(),
            headers=_auth_header(plaintext),
        )
        assert session_resp.status_code == 201, session_resp.text
        session_id = session_resp.json()["id"]

        create_resp = client.post(
            "/api/v1/external-results/case",
            json={
                "session_id": session_id,
                "external_id": f"TC-art-{uuid.uuid4()}",
                "title": "Artifact test case",
                "outcome": "passed",
                "duration_ms": 30,
                "requirement_ids": [],
            },
            headers=_auth_header(plaintext),
        )
        assert create_resp.status_code == 201, create_resp.text
        case_id = create_resp.json()["id"]

        png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
        upload_resp = client.post(
            "/api/v1/external-results/artifact",
            data={"case_result_id": case_id, "kind": "screenshot", "filename": "test.png"},
            files={"file": ("test.png", io.BytesIO(png_bytes), "image/png")},
            headers=_auth_header(plaintext),
        )

    assert upload_resp.status_code == 201, upload_resp.text
    artifact_audit = next((c for c in captured if c["action"] == "external_results.artifact.upload"), None)
    assert artifact_audit is not None
    details = artifact_audit["details"]
    assert "case_result_id" in details
    assert "kind" in details
    assert "filename" in details
    assert "content_type" in details
    assert "size_bytes" in details


# ---------------------------------------------------------------------------
# Regression-proof enforcement test
# ---------------------------------------------------------------------------

# Endpoints that intentionally do NOT audit (reads):
_READ_ONLY_OPS = frozenset(
    {
        ("GET", "/external-results/session/{session_id}"),
        ("GET", "/external-results/case/{case_result_id}"),
    }
)


def _state_changing_routes():
    """Yield (method, path, route) for every non-GET endpoint in the router."""
    for route in external_results_router.routes:
        if not hasattr(route, "methods"):
            continue
        for method in route.methods:
            if method == "HEAD":
                continue
            if (method, route.path) in _READ_ONLY_OPS:
                continue
            if method == "GET":
                continue
            yield method, route.path, route


@pytest.mark.parametrize("method,path,_route", list(_state_changing_routes()))
def test_state_changing_endpoint_emits_audit(monkeypatch, db_session, write_token, method, path, _route):
    """Every state-changing endpoint MUST call write_audit at least once.

    If a new endpoint is added without an audit call, this test fails by default
    — that's the point. To intentionally skip auditing on a new read endpoint,
    add it to _READ_ONLY_OPS.
    """
    captured: list[dict] = []

    async def fake_write_audit(db, **kwargs):
        captured.append(kwargs)
        return SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr("app.api.external_results.write_audit", fake_write_audit)

    # Mock storage for the artifact upload endpoint.
    _fake_storage_result = StorageResult(
        key="enf/test.png",
        url="http://example.com/enf/test.png",
        size_bytes=72,
        content_type="image/png",
    )
    monkeypatch.setattr(
        "app.api.external_results.get_storage",
        lambda: SimpleNamespace(save=lambda stream, *, key, content_type: _fake_storage_result),
    )

    token_model, plaintext = write_token
    headers = _auth_header(plaintext)

    with TestClient(app) as client:

        def _create_session_id() -> str:
            r = client.post("/api/v1/external-results/session", json=_session_payload(), headers=headers)
            assert r.status_code == 201, r.text
            return r.json()["id"]

        def _create_case_id(session_id: str) -> str:
            r = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"enf-{uuid.uuid4()}",
                    "title": "enforcement test case",
                    "outcome": "passed",
                    "duration_ms": 5,
                    "requirement_ids": [],
                },
                headers=headers,
            )
            assert r.status_code == 201, r.text
            return r.json()["id"]

        # Drive the endpoint with a happy-path call.
        # captured.clear() is called immediately before each actual endpoint call so that
        # prerequisite setup calls (which also invoke fake_write_audit) do not mask a
        # missing write_audit on the endpoint under test.
        if (method, path) == ("POST", "/external-results/session"):
            captured.clear()
            resp = client.post("/api/v1/external-results/session", json=_session_payload(), headers=headers)

        elif (method, path) == ("PATCH", "/external-results/session/{session_id}"):
            session_id = _create_session_id()
            captured.clear()
            resp = client.patch(
                f"/api/v1/external-results/session/{session_id}",
                json={"status": "passed", "summary": {"total": 1, "passed": 1}},
                headers=headers,
            )

        elif (method, path) == ("POST", "/external-results/case"):
            session_id = _create_session_id()
            captured.clear()
            resp = client.post(
                "/api/v1/external-results/case",
                json={
                    "session_id": session_id,
                    "external_id": f"enf-{uuid.uuid4()}",
                    "title": "enforcement test case",
                    "outcome": "passed",
                    "duration_ms": 5,
                    "requirement_ids": [],
                },
                headers=headers,
            )

        elif (method, path) == ("PATCH", "/external-results/case/{case_result_id}"):
            session_id = _create_session_id()
            case_id = _create_case_id(session_id)
            captured.clear()
            resp = client.patch(
                f"/api/v1/external-results/case/{case_id}",
                json={"outcome": "flaky"},
                headers=headers,
            )

        elif (method, path) == ("POST", "/external-results/artifact"):
            session_id = _create_session_id()
            case_id = _create_case_id(session_id)
            captured.clear()
            png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
            resp = client.post(
                "/api/v1/external-results/artifact",
                data={"case_result_id": case_id, "kind": "screenshot", "filename": "test.png"},
                files={"file": ("test.png", io.BytesIO(png_bytes), "image/png")},
                headers=headers,
            )

        else:
            raise AssertionError(
                f"No dispatch driver for {method} {path}. "
                "Add a happy-path driver to test_state_changing_endpoint_emits_audit."
            )

    assert resp.status_code in (200, 201), f"{method} {path} returned {resp.status_code}: {resp.text}"
    assert len(captured) >= 1, (
        f"{method} {path} did not call write_audit. "
        f"Every state-changing External Results endpoint must emit an audit entry. "
        f"If this endpoint is intentionally read-only, add it to _READ_ONLY_OPS."
    )
