"""Tests for the Notification system"""

import uuid

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.crud.notification import (
    create_notification,
    create_notification_for_all_users,
    get_notifications,
    get_unread_count,
    mark_all_as_read,
    mark_as_read,
)
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.notification import NotificationType
from app.models.user import User, UserRole

# ── Fixtures ───────────────────────────────────────────────────────────────────


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


def _make_user(role: UserRole = UserRole.reviewer) -> User:
    return User(
        id=uuid.uuid4(),
        email=f"{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        full_name="Test User",
        role=role,
        is_active=True,
    )


# ── CRUD tests ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_notification(db_session):
    """Creating a notification persists to the database."""
    user = _make_user()
    db_session.add(user)
    await db_session.commit()

    notification = await create_notification(
        db_session,
        user_id=user.id,
        type=NotificationType.REQUIREMENT_CREATED,
        title="New Requirement",
        message="A requirement was created",
        metadata={"requirement_id": str(uuid.uuid4())},
    )

    assert notification.id is not None
    assert notification.user_id == user.id
    assert notification.type == NotificationType.REQUIREMENT_CREATED
    assert notification.title == "New Requirement"
    assert notification.read is False


@pytest.mark.asyncio
async def test_list_notifications_only_own(db_session):
    """get_notifications returns only the requesting user's notifications."""
    user1 = _make_user()
    user2 = _make_user()
    db_session.add_all([user1, user2])
    await db_session.commit()

    await create_notification(
        db_session, user_id=user1.id, type=NotificationType.TEST_CASE_CREATED, title="T1", message="m1"
    )
    await create_notification(
        db_session, user_id=user2.id, type=NotificationType.TEST_CASE_CREATED, title="T2", message="m2"
    )

    notifications, total = await get_notifications(db_session, user_id=user1.id)
    assert total == 1
    assert len(notifications) == 1
    assert notifications[0].user_id == user1.id


@pytest.mark.asyncio
async def test_get_unread_count(db_session):
    """get_unread_count returns correct count."""
    user = _make_user()
    db_session.add(user)
    await db_session.commit()

    await create_notification(
        db_session, user_id=user.id, type=NotificationType.SUGGESTION_REVIEWED, title="T", message="m"
    )
    await create_notification(
        db_session, user_id=user.id, type=NotificationType.SUGGESTION_REVIEWED, title="T2", message="m2"
    )

    count = await get_unread_count(db_session, user_id=user.id)
    assert count == 2

    first_id = await _get_first_notification_id(db_session, user.id)
    await mark_as_read(db_session, notification_id=first_id, user_id=user.id)
    count = await get_unread_count(db_session, user_id=user.id)
    assert count == 1


async def _get_first_notification_id(db_session, user_id):
    notifications, _ = await get_notifications(db_session, user_id=user_id)
    return notifications[0].id


@pytest.mark.asyncio
async def test_mark_as_read_own_notification(db_session):
    """mark_as_read marks a notification as read for the owner."""
    user = _make_user()
    db_session.add(user)
    await db_session.commit()

    notification = await create_notification(
        db_session, user_id=user.id, type=NotificationType.SUGGESTIONS_GENERATED, title="T", message="m"
    )
    assert notification.read is False

    updated = await mark_as_read(db_session, notification_id=notification.id, user_id=user.id)
    assert updated is not None
    assert updated.read is True


@pytest.mark.asyncio
async def test_mark_as_read_other_users_notification_fails(db_session):
    """mark_as_read returns None when user doesn't own the notification."""
    user1 = _make_user()
    user2 = _make_user()
    db_session.add_all([user1, user2])
    await db_session.commit()

    notification = await create_notification(
        db_session, user_id=user1.id, type=NotificationType.REQUIREMENT_CREATED, title="T", message="m"
    )

    result = await mark_as_read(db_session, notification_id=notification.id, user_id=user2.id)
    assert result is None


@pytest.mark.asyncio
async def test_mark_all_as_read(db_session):
    """mark_all_as_read marks all user's notifications as read."""
    user = _make_user()
    db_session.add(user)
    await db_session.commit()

    for _ in range(3):
        await create_notification(
            db_session, user_id=user.id, type=NotificationType.TEST_CASE_CREATED, title="T", message="m"
        )

    count = await mark_all_as_read(db_session, user_id=user.id)
    assert count == 3

    unread = await get_unread_count(db_session, user_id=user.id)
    assert unread == 0


@pytest.mark.asyncio
async def test_create_notification_for_all_users(db_session):
    """create_notification_for_all_users creates notifications for every active user."""
    users = [_make_user() for _ in range(3)]
    db_session.add_all(users)
    await db_session.commit()

    notifications = await create_notification_for_all_users(
        db_session,
        type=NotificationType.COVERAGE_DROP,
        title="Coverage Drop",
        message="Coverage dropped",
    )
    assert len(notifications) == 3


@pytest.mark.asyncio
async def test_create_notification_for_all_users_excludes_creator(db_session):
    """create_notification_for_all_users can exclude one user."""
    users = [_make_user() for _ in range(3)]
    db_session.add_all(users)
    await db_session.commit()

    creator = users[0]
    notifications = await create_notification_for_all_users(
        db_session,
        type=NotificationType.REQUIREMENT_CREATED,
        title="New Req",
        message="msg",
        exclude_user_id=creator.id,
    )
    assert len(notifications) == 2
    assert all(n.user_id != creator.id for n in notifications)


# ── API endpoint tests ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_notifications_endpoint(db_session):
    """GET /notifications returns current user's notifications."""
    user = _make_user()
    db_session.add(user)
    await db_session.commit()

    await create_notification(
        db_session, user_id=user.id, type=NotificationType.REQUIREMENT_CREATED, title="T", message="m"
    )

    async def override_user():
        return user

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/notifications")
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        assert "total" in data
        assert data["total"] == 1
        assert data["unread_count"] == 1
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_unread_count_endpoint(db_session):
    """GET /notifications/unread-count returns correct unread count."""
    user = _make_user()
    db_session.add(user)
    await db_session.commit()

    await create_notification(
        db_session, user_id=user.id, type=NotificationType.TEST_CASE_CREATED, title="T", message="m"
    )

    async def override_user():
        return user

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/notifications/unread-count")
        assert response.status_code == 200
        assert response.json()["unread_count"] == 1
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_mark_notification_read_endpoint(db_session):
    """PATCH /notifications/{id}/read marks a notification as read."""
    user = _make_user()
    db_session.add(user)
    await db_session.commit()

    notification = await create_notification(
        db_session, user_id=user.id, type=NotificationType.SUGGESTIONS_GENERATED, title="T", message="m"
    )

    async def override_user():
        return user

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            response = client.patch(f"/api/v1/notifications/{notification.id}/read")
        assert response.status_code == 200
        assert response.json()["read"] is True
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_mark_all_read_endpoint(db_session):
    """POST /notifications/mark-all-read marks all as read."""
    user = _make_user()
    db_session.add(user)
    await db_session.commit()

    for _ in range(2):
        await create_notification(
            db_session, user_id=user.id, type=NotificationType.TEST_CASE_CREATED, title="T", message="m"
        )

    async def override_user():
        return user

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/notifications/mark-all-read")
        assert response.status_code == 200
        assert response.json()["marked_read"] == 2
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_unauthenticated_access_returns_401(db_session):
    """Unauthenticated requests to notification endpoints return 401."""
    with TestClient(app) as client:
        response = client.get("/api/v1/notifications")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_notification_on_requirement_creation(db_session):
    """Creating a requirement via the API produces notifications for other users."""
    creator = _make_user(UserRole.admin)
    other_user = _make_user(UserRole.reviewer)
    db_session.add_all([creator, other_user])
    await db_session.commit()

    async def override_creator():
        return creator

    app.dependency_overrides[get_current_user] = override_creator
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/requirements",
                json={
                    "title": "Notification Test Req",
                    "description": "For notification test",
                    "type": "functional",
                    "priority": "medium",
                },
            )
        assert response.status_code == 201

        # Other user should have received a notification
        notifications, total = await get_notifications(db_session, user_id=other_user.id)
        assert total >= 1
        assert any(n.type == NotificationType.REQUIREMENT_CREATED for n in notifications)
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_notification_on_test_case_creation(db_session):
    """Creating a test case via the API produces notifications for other users."""
    creator = _make_user(UserRole.admin)
    other_user = _make_user(UserRole.reviewer)
    db_session.add_all([creator, other_user])
    await db_session.commit()

    async def override_creator():
        return creator

    app.dependency_overrides[get_current_user] = override_creator
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/test-cases",
                json={
                    "title": "Notification Test TC",
                    "description": "For notification test",
                    "type": "functional",
                    "priority": "medium",
                },
            )
        assert response.status_code == 201

        notifications, total = await get_notifications(db_session, user_id=other_user.id)
        assert total >= 1
        assert any(n.type == NotificationType.TEST_CASE_CREATED for n in notifications)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
