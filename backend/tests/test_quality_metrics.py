from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.crud.quality_metrics import (
    get_automation_coverage,
    get_defect_trend,
    get_defects_by_module,
    get_pass_rate_trend,
    get_quality_dashboard_snapshot,
    get_summary_stats,
)
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
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@example.com",
            hashed_password="hashed",
            full_name="Admin User",
            role=UserRole.admin,
            is_active=True,
        )
        session.add(admin_user)
        await session.commit()

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        yield session, admin_user
        app.dependency_overrides.clear()

    await engine.dispose()


async def _seed_quality_data(session: AsyncSession, admin_user: User) -> None:
    requirement_auth = Requirement(
        id=uuid.uuid4(),
        external_id="REQ-001",
        title="Authentication",
        description="desc",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.CRITICAL,
        status=RequirementStatus.APPROVED,
        module="Authentication",
    )
    requirement_orders = Requirement(
        id=uuid.uuid4(),
        external_id="REQ-002",
        title="Orders",
        description="desc",
        type=RequirementType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=RequirementStatus.APPROVED,
        module="Orders",
    )

    auth_case = TestCase(
        id=uuid.uuid4(),
        external_id="TC-001",
        title="Auth login",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.CRITICAL,
        status=TestCaseStatus.READY,
        module="Authentication",
        automation_status=AutomationStatus.AUTOMATED,
    )
    search_case = TestCase(
        id=uuid.uuid4(),
        external_id="TC-002",
        title="Search filters",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        module="Product",
        automation_status=AutomationStatus.AUTOMATABLE,
    )
    orders_case = TestCase(
        id=uuid.uuid4(),
        external_id="TC-003",
        title="Refund review",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.READY,
        module="Orders",
        automation_status=AutomationStatus.MANUAL,
    )

    session.add_all([requirement_auth, requirement_orders, auth_case, search_case, orders_case])
    await session.flush()

    session.add_all(
        [
            RequirementTestCaseLink(
                id=uuid.uuid4(),
                requirement_id=requirement_auth.id,
                test_case_id=auth_case.id,
                link_type=LinkType.COVERS,
                link_source=LinkSource.MANUAL,
                created_by="seed",
            ),
            RequirementTestCaseLink(
                id=uuid.uuid4(),
                requirement_id=requirement_orders.id,
                test_case_id=orders_case.id,
                link_type=LinkType.COVERS,
                link_source=LinkSource.MANUAL,
                created_by="seed",
            ),
        ]
    )

    project = Project(id=uuid.uuid4(), name="ShopFlow", description="seed")
    session.add(project)
    await session.flush()

    runner_token = RunnerToken(
        id=uuid.uuid4(),
        hashed_token="seed-token-hash",
        salt="seed-token-salt",
        label="seed-runner",
        scopes=["external_results:write"],
        created_by_user_id=admin_user.id,
        created_at=_days_ago(40),
    )
    session.add(runner_token)
    await session.flush()

    session_a = ExternalRunSession(
        id=uuid.uuid4(),
        project_id=project.id,
        runner="@bgstm/playwright-core@0.1.0",
        status=RunStatus.failed,
        git_sha="run-a",
        git_branch="main",
        ci_url="https://ci.example.com/runs/a",
        run_metadata={"os": "linux"},
        summary={"total": 3, "failed": 2},
        started_at=_days_ago(20),
        finished_at=_days_ago(20) + timedelta(minutes=5),
        created_by_runner_token_id=runner_token.id,
    )
    session_b = ExternalRunSession(
        id=uuid.uuid4(),
        project_id=project.id,
        runner="@bgstm/playwright-core@0.1.0",
        status=RunStatus.failed,
        git_sha="run-b",
        git_branch="main",
        ci_url="https://ci.example.com/runs/b",
        run_metadata={"os": "linux"},
        summary={"total": 3, "failed": 1},
        started_at=_days_ago(5),
        finished_at=_days_ago(5) + timedelta(minutes=6),
        created_by_runner_token_id=runner_token.id,
    )
    session.add_all([session_a, session_b])
    await session.flush()

    session.add_all(
        [
            ExternalCaseResult(
                id=uuid.uuid4(),
                session_id=session_a.id,
                test_case_id=auth_case.id,
                external_id="TC-001-a",
                title=auth_case.title,
                outcome=CaseStatus.failed,
                duration_ms=1000,
                error_message="failed",
                created_at=_days_ago(20),
                updated_at=_days_ago(20),
            ),
            ExternalCaseResult(
                id=uuid.uuid4(),
                session_id=session_a.id,
                test_case_id=search_case.id,
                external_id="TC-002-a",
                title=search_case.title,
                outcome=CaseStatus.failed,
                duration_ms=1000,
                error_message="failed",
                created_at=_days_ago(20),
                updated_at=_days_ago(20),
            ),
            ExternalCaseResult(
                id=uuid.uuid4(),
                session_id=session_a.id,
                test_case_id=orders_case.id,
                external_id="TC-003-a",
                title=orders_case.title,
                outcome=CaseStatus.passed,
                duration_ms=1000,
                created_at=_days_ago(20),
                updated_at=_days_ago(20),
            ),
            ExternalCaseResult(
                id=uuid.uuid4(),
                session_id=session_b.id,
                test_case_id=auth_case.id,
                external_id="TC-001-b",
                title=auth_case.title,
                outcome=CaseStatus.failed,
                duration_ms=1000,
                error_message="failed-again",
                created_at=_days_ago(5),
                updated_at=_days_ago(5),
            ),
            ExternalCaseResult(
                id=uuid.uuid4(),
                session_id=session_b.id,
                test_case_id=search_case.id,
                external_id="TC-002-b",
                title=search_case.title,
                outcome=CaseStatus.passed,
                duration_ms=1000,
                created_at=_days_ago(5),
                updated_at=_days_ago(5),
            ),
            ExternalCaseResult(
                id=uuid.uuid4(),
                session_id=session_b.id,
                test_case_id=orders_case.id,
                external_id="TC-003-b",
                title=orders_case.title,
                outcome=CaseStatus.passed,
                duration_ms=1000,
                created_at=_days_ago(5),
                updated_at=_days_ago(5),
            ),
        ]
    )
    await session.commit()


@pytest.mark.asyncio
async def test_quality_metric_crud_empty_db_returns_zeroed_shapes(db_session):
    session, _admin_user = db_session

    defect_trend = await get_defect_trend(session, 30)
    pass_rate_trend = await get_pass_rate_trend(session, 30)
    defects_by_module = await get_defects_by_module(session, 30)
    automation_coverage = await get_automation_coverage(session)
    summary_stats = await get_summary_stats(session)

    assert len(defect_trend.points) == 30
    assert defect_trend.is_synthetic is True
    assert all(point.total == 0 for point in defect_trend.points)

    assert len(pass_rate_trend.points) == 30
    assert pass_rate_trend.is_synthetic is True
    assert all(point.total_executed == 0 for point in pass_rate_trend.points)

    assert defects_by_module.modules == []
    assert automation_coverage.total == 0
    assert automation_coverage.percent_automated == 0.0
    assert summary_stats.defect_removal_efficiency_pct is None
    assert summary_stats.mean_time_to_repair_hours is None
    assert summary_stats.escape_rate_pct is None
    assert summary_stats.total_defects_30d == 0
    assert summary_stats.open_critical_defects == 0


@pytest.mark.asyncio
async def test_quality_metric_crud_seeded_paths_return_expected_values(db_session):
    session, admin_user = db_session
    await _seed_quality_data(session, admin_user)

    defect_trend = await get_defect_trend(session, 30)
    pass_rate_trend = await get_pass_rate_trend(session, 30)
    defects_by_module = await get_defects_by_module(session, 30)
    automation_coverage = await get_automation_coverage(session)
    summary_stats = await get_summary_stats(session)
    snapshot = await get_quality_dashboard_snapshot(session)

    assert defect_trend.is_synthetic is False
    assert sum(point.total for point in defect_trend.points) == 3
    assert any(point.by_severity.critical > 0 for point in defect_trend.points)
    assert any(point.total_executed > 0 for point in pass_rate_trend.points)
    assert any(point.pass_rate_pct < 100 for point in pass_rate_trend.points)
    assert [bucket.module for bucket in defects_by_module.modules] == ["Authentication", "Product"]
    assert automation_coverage.total == 3
    assert automation_coverage.automated == 1
    assert automation_coverage.manual == 1
    assert automation_coverage.in_progress == 1
    assert automation_coverage.percent_automated == pytest.approx(33.33, abs=0.01)
    assert summary_stats.total_defects_30d == 3
    assert summary_stats.open_critical_defects == 1
    assert snapshot.window_days == 30
    assert snapshot.defect_trend.points
    assert snapshot.pass_rate_trend.points
    assert snapshot.defects_by_module.modules


@pytest.mark.asyncio
async def test_quality_dashboard_snapshot_endpoint_returns_all_sections(db_session):
    session, admin_user = db_session
    await _seed_quality_data(session, admin_user)

    async def override_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/quality-metrics/")
        assert response.status_code == 200
        payload = response.json()
        assert set(payload.keys()) >= {
            "generated_at",
            "window_days",
            "defect_trend",
            "pass_rate_trend",
            "defects_by_module",
            "automation_coverage",
            "summary_stats",
        }
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_quality_metric_window_validation_returns_422(db_session):
    _session, admin_user = db_session

    async def override_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/quality-metrics/defect-trend?window=14")
        assert response.status_code == 422
    finally:
        app.dependency_overrides.pop(get_current_user, None)
