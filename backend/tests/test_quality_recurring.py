from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.dependencies import get_current_user
from app.crud.quality_recurring import get_recurring_defects_pareto
from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.external_case_result import CaseStatus, ExternalCaseResult
from app.models.external_results import ExternalRunSession, RunStatus
from app.models.project import Project
from app.models.requirement import PriorityLevel
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


async def _seed_recurring_failures(session: AsyncSession, admin_user: User):
    checkout_case = TestCase(
        id=uuid.uuid4(),
        external_id="TC-CHECKOUT",
        title="Checkout flow",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.CRITICAL,
        status=TestCaseStatus.READY,
        module="Checkout",
        automation_status=AutomationStatus.AUTOMATED,
    )
    refund_case = TestCase(
        id=uuid.uuid4(),
        external_id="TC-REFUND",
        title="Refund review",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.HIGH,
        status=TestCaseStatus.READY,
        module="Orders",
        automation_status=AutomationStatus.AUTOMATED,
    )
    one_off_case = TestCase(
        id=uuid.uuid4(),
        external_id="TC-SEARCH",
        title="Search filters",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.READY,
        module="Search",
        automation_status=AutomationStatus.AUTOMATED,
    )
    session.add_all([checkout_case, refund_case, one_off_case])

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

    run_20d = ExternalRunSession(
        id=uuid.uuid4(),
        project_id=project.id,
        runner="@bgstm/playwright-core@0.1.0",
        status=RunStatus.failed,
        git_sha="run-20d",
        git_branch="main",
        run_metadata={},
        summary={"total": 3, "failed": 3},
        started_at=_days_ago(20),
        finished_at=_days_ago(20) + timedelta(minutes=1),
        created_by_runner_token_id=runner_token.id,
    )
    run_5d = ExternalRunSession(
        id=uuid.uuid4(),
        project_id=project.id,
        runner="@bgstm/playwright-core@0.1.0",
        status=RunStatus.failed,
        git_sha="run-5d",
        git_branch="main",
        run_metadata={},
        summary={"total": 2, "failed": 2},
        started_at=_days_ago(5),
        finished_at=_days_ago(5) + timedelta(minutes=1),
        created_by_runner_token_id=runner_token.id,
    )
    run_2d = ExternalRunSession(
        id=uuid.uuid4(),
        project_id=project.id,
        runner="@bgstm/playwright-core@0.1.0",
        status=RunStatus.failed,
        git_sha="run-2d",
        git_branch="main",
        run_metadata={},
        summary={"total": 1, "failed": 1},
        started_at=_days_ago(2),
        finished_at=_days_ago(2) + timedelta(minutes=1),
        created_by_runner_token_id=runner_token.id,
    )
    session.add_all([run_20d, run_5d, run_2d])
    await session.flush()

    def failure(run: ExternalRunSession, test_case: TestCase, days: int) -> ExternalCaseResult:
        return ExternalCaseResult(
            id=uuid.uuid4(),
            session_id=run.id,
            test_case_id=test_case.id,
            external_id=f"{test_case.external_id}-{days}",
            title=test_case.title,
            outcome=CaseStatus.failed,
            duration_ms=500,
            error_message="failed",
            created_at=_days_ago(days),
            updated_at=_days_ago(days),
        )

    session.add_all(
        [
            failure(run_20d, checkout_case, 20),
            failure(run_5d, checkout_case, 5),
            failure(run_2d, checkout_case, 2),
            failure(run_20d, refund_case, 20),
            failure(run_5d, refund_case, 5),
            failure(run_20d, one_off_case, 20),
        ]
    )
    await session.commit()
    return checkout_case, refund_case, run_2d


@pytest.mark.asyncio
async def test_recurring_defects_pareto_ranks_repeated_failures_and_excludes_one_offs(db_session):
    session, admin_user = db_session
    checkout_case, refund_case, latest_checkout_run = await _seed_recurring_failures(session, admin_user)

    result = await get_recurring_defects_pareto(session, 30)

    assert result.total_recurring_failures == 5
    assert [entry.test_case_id for entry in result.entries] == [checkout_case.id, refund_case.id]
    assert [entry.failure_count for entry in result.entries] == [3, 2]
    assert [entry.cumulative_pct for entry in result.entries] == [60.0, 100.0]
    assert result.entries[0].module == "Checkout"
    assert result.entries[0].latest_failure_session_id == latest_checkout_run.id


@pytest.mark.asyncio
async def test_recurring_defects_pareto_honors_selected_window(db_session):
    session, admin_user = db_session
    checkout_case, _refund_case, _latest_checkout_run = await _seed_recurring_failures(session, admin_user)

    result = await get_recurring_defects_pareto(session, 7)

    assert result.total_recurring_failures == 2
    assert len(result.entries) == 1
    assert result.entries[0].test_case_id == checkout_case.id
    assert result.entries[0].failure_count == 2
    assert result.entries[0].cumulative_pct == 100.0


@pytest.mark.asyncio
async def test_recurring_defects_endpoint_supports_top_n(db_session):
    session, admin_user = db_session
    await _seed_recurring_failures(session, admin_user)

    async def override_user():
        return admin_user

    app.dependency_overrides[get_current_user] = override_user
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/quality-metrics/recurring-defects?window=30&top_n=1")
        assert response.status_code == 200
        payload = response.json()
        assert payload["total_recurring_failures"] == 5
        assert len(payload["entries"]) == 1
        assert payload["entries"][0]["failure_count"] == 3
    finally:
        app.dependency_overrides.pop(get_current_user, None)
