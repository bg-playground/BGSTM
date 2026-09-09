from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.crud.quality_module_risk import get_module_coverage_failure_density
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.external_case_result import CaseStatus, ExternalCaseResult
from app.models.external_results import ExternalRunSession, RunStatus
from app.models.link import LinkSource, LinkType, RequirementTestCaseLink
from app.models.project import Project
from app.models.requirement import PriorityLevel, Requirement, RequirementStatus, RequirementType
from app.models.runner_token import RunnerToken
from app.models.test_case import AutomationStatus, TestCase, TestCaseStatus, TestCaseType
from app.models.user import User, UserRole


def _days_ago(days: int) -> datetime:
    return (datetime.now(timezone.utc) - timedelta(days=days)).replace(tzinfo=None)


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        user = User(
            id=uuid.uuid4(),
            email="admin@example.com",
            hashed_password="hashed",
            full_name="Admin",
            role=UserRole.admin,
            is_active=True,
        )
        session.add(user)
        await session.commit()

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        yield session, user
        app.dependency_overrides.clear()

    await engine.dispose()


async def _seed(session: AsyncSession, user: User) -> None:
    auth_covered = Requirement(
        id=uuid.uuid4(), external_id="REQ-A1", title="Auth login", description="desc",
        type=RequirementType.FUNCTIONAL, priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED, module="Authentication",
    )
    auth_uncovered = Requirement(
        id=uuid.uuid4(), external_id="REQ-A2", title="Auth lockout", description="desc",
        type=RequirementType.FUNCTIONAL, priority=PriorityLevel.HIGH,
        status=RequirementStatus.APPROVED, module="Authentication",
    )
    orders_covered = Requirement(
        id=uuid.uuid4(), external_id="REQ-O1", title="Order submit", description="desc",
        type=RequirementType.FUNCTIONAL, priority=PriorityLevel.CRITICAL,
        status=RequirementStatus.APPROVED, module="Orders",
    )
    billing_uncovered = Requirement(
        id=uuid.uuid4(), external_id="REQ-B1", title="Billing history", description="desc",
        type=RequirementType.FUNCTIONAL, priority=PriorityLevel.MEDIUM,
        status=RequirementStatus.APPROVED, module="Billing",
    )
    auth_case = TestCase(
        id=uuid.uuid4(), external_id="TC-A1", title="Login", description="desc",
        type=TestCaseType.FUNCTIONAL, priority=PriorityLevel.HIGH, status=TestCaseStatus.READY,
        module="Authentication", automation_status=AutomationStatus.AUTOMATED,
    )
    orders_case = TestCase(
        id=uuid.uuid4(), external_id="TC-O1", title="Submit order", description="desc",
        type=TestCaseType.FUNCTIONAL, priority=PriorityLevel.CRITICAL, status=TestCaseStatus.READY,
        module="Orders", automation_status=AutomationStatus.AUTOMATED,
    )
    session.add_all([auth_covered, auth_uncovered, orders_covered, billing_uncovered, auth_case, orders_case])
    await session.flush()

    session.add_all([
        RequirementTestCaseLink(
            id=uuid.uuid4(), requirement_id=auth_covered.id, test_case_id=auth_case.id,
            link_type=LinkType.COVERS, link_source=LinkSource.MANUAL, created_by="seed",
        ),
        RequirementTestCaseLink(
            id=uuid.uuid4(), requirement_id=orders_covered.id, test_case_id=orders_case.id,
            link_type=LinkType.COVERS, link_source=LinkSource.AI_CONFIRMED, created_by="seed",
        ),
    ])

    project = Project(id=uuid.uuid4(), name="ShopFlow", description="seed")
    session.add(project)
    await session.flush()
    token = RunnerToken(
        id=uuid.uuid4(), hashed_token="hash", salt="salt", label="seed",
        scopes=["external_results:write"], created_by_user_id=user.id, created_at=_days_ago(40),
    )
    session.add(token)
    await session.flush()

    recent_run = ExternalRunSession(
        id=uuid.uuid4(), project_id=project.id, runner="pytest", status=RunStatus.failed,
        git_sha="recent", git_branch="main", run_metadata={}, summary={"total": 4, "failed": 3},
        started_at=_days_ago(3), finished_at=_days_ago(3) + timedelta(minutes=1),
        created_by_runner_token_id=token.id,
    )
    old_run = ExternalRunSession(
        id=uuid.uuid4(), project_id=project.id, runner="pytest", status=RunStatus.failed,
        git_sha="old", git_branch="main", run_metadata={}, summary={"total": 1, "failed": 1},
        started_at=_days_ago(20), finished_at=_days_ago(20) + timedelta(minutes=1),
        created_by_runner_token_id=token.id,
    )
    session.add_all([recent_run, old_run])
    await session.flush()

    outcomes = [
        (recent_run.id, auth_case, CaseStatus.failed, 3),
        (recent_run.id, auth_case, CaseStatus.passed, 3),
        (recent_run.id, orders_case, CaseStatus.failed, 3),
        (recent_run.id, orders_case, CaseStatus.failed, 3),
        (old_run.id, auth_case, CaseStatus.failed, 20),
    ]
    for index, (run_id, test_case, outcome, age) in enumerate(outcomes):
        session.add(ExternalCaseResult(
            id=uuid.uuid4(), session_id=run_id, test_case_id=test_case.id,
            external_id=f"{test_case.external_id}-{index}", title=test_case.title,
            outcome=outcome, duration_ms=100, created_at=_days_ago(age), updated_at=_days_ago(age),
        ))
    await session.commit()


@pytest.mark.asyncio
async def test_module_risk_combines_coverage_and_normalized_failures(db_session):
    session, user = db_session
    await _seed(session, user)

    response = await get_module_coverage_failure_density(session, 7)
    points = {point.module: point for point in response.points}

    assert points["Authentication"].coverage_pct == 50.0
    assert points["Authentication"].covered_requirements == 1
    assert points["Authentication"].total_requirements == 2
    assert points["Authentication"].total_executions == 2
    assert points["Authentication"].total_failures == 1
    assert points["Authentication"].failure_density_pct == 50.0

    assert points["Orders"].coverage_pct == 100.0
    assert points["Orders"].failure_density_pct == 100.0
    assert points["Orders"].total_failures == 2

    assert points["Billing"].coverage_pct == 0.0
    assert points["Billing"].total_executions == 0
    assert points["Billing"].failure_density_pct == 0.0

    assert response.median_coverage_pct == 50.0
    assert response.median_failure_density_pct == 50.0


@pytest.mark.asyncio
async def test_module_risk_window_excludes_old_execution(db_session):
    session, user = db_session
    await _seed(session, user)

    seven_day = await get_module_coverage_failure_density(session, 7)
    ninety_day = await get_module_coverage_failure_density(session, 90)
    seven_auth = next(point for point in seven_day.points if point.module == "Authentication")
    ninety_auth = next(point for point in ninety_day.points if point.module == "Authentication")

    assert seven_auth.total_executions == 2
    assert seven_auth.total_failures == 1
    assert ninety_auth.total_executions == 3
    assert ninety_auth.total_failures == 2
    assert ninety_auth.failure_density_pct == pytest.approx(66.67)


def test_coverage_vs_defects_endpoint_and_window_validation(db_session):
    session, user = db_session

    async def override_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_current_user
    with TestClient(app) as client:
        response = client.get("/api/quality-metrics/coverage-vs-defects?window=7")
        invalid = client.get("/api/quality-metrics/coverage-vs-defects?window=14")

    assert response.status_code == 200
    assert response.json()["points"] == []
    assert invalid.status_code == 422
