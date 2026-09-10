from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.crud.quality_recovery import get_recovery_trend
from app.models.base import Base
from app.models.external_case_result import CaseStatus, ExternalCaseResult
from app.models.external_results import ExternalRunSession, RunStatus
from app.models.project import Project
from app.models.requirement import PriorityLevel
from app.models.runner_token import RunnerToken
from app.models.test_case import AutomationStatus, TestCase, TestCaseStatus, TestCaseType
from app.models.user import User, UserRole


def _days_ago(days: float) -> datetime:
    return (datetime.now(timezone.utc) - timedelta(days=days)).replace(tzinfo=None)


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


async def _seed_context(session: AsyncSession):
    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        hashed_password="hashed",
        full_name="Admin",
        role=UserRole.admin,
        is_active=True,
    )
    project = Project(id=uuid.uuid4(), name="Recovery", description="seed")
    session.add_all([user, project])
    await session.flush()
    token = RunnerToken(
        id=uuid.uuid4(),
        hashed_token="hash",
        salt="salt",
        label="runner",
        scopes=["external_results:write"],
        created_by_user_id=user.id,
        created_at=_days_ago(40),
    )
    session.add(token)
    await session.flush()
    return project, token


async def _case(session: AsyncSession, external_id: str, module: str, priority: PriorityLevel) -> TestCase:
    case = TestCase(
        id=uuid.uuid4(),
        external_id=external_id,
        title=external_id,
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=priority,
        status=TestCaseStatus.READY,
        module=module,
        automation_status=AutomationStatus.AUTOMATED,
    )
    session.add(case)
    await session.flush()
    return case


async def _result(
    session: AsyncSession,
    project: Project,
    token: RunnerToken,
    case: TestCase,
    *,
    days_ago: float,
    outcome: CaseStatus,
) -> None:
    at = _days_ago(days_ago)
    run = ExternalRunSession(
        id=uuid.uuid4(),
        project_id=project.id,
        runner="pytest",
        status=RunStatus.failed,
        git_sha=str(uuid.uuid4()),
        git_branch="main",
        run_metadata={},
        summary={},
        started_at=at,
        finished_at=at + timedelta(minutes=1),
        created_by_runner_token_id=token.id,
    )
    session.add(run)
    await session.flush()
    session.add(
        ExternalCaseResult(
            id=uuid.uuid4(),
            session_id=run.id,
            test_case_id=case.id,
            external_id=case.external_id,
            title=case.title,
            outcome=outcome,
            duration_ms=100,
            created_at=at,
            updated_at=at,
        )
    )
    await session.flush()


@pytest.mark.asyncio
async def test_recovery_uses_first_failure_until_first_subsequent_pass(db_session):
    session = db_session
    project, token = await _seed_context(session)
    case = await _case(session, "TC-CHECKOUT", "Checkout", PriorityLevel.CRITICAL)
    await _result(session, project, token, case, days_ago=5, outcome=CaseStatus.failed)
    await _result(session, project, token, case, days_ago=4, outcome=CaseStatus.failed)
    await _result(session, project, token, case, days_ago=3, outcome=CaseStatus.flaky)
    await _result(session, project, token, case, days_ago=2, outcome=CaseStatus.passed)
    await session.commit()

    result = await get_recovery_trend(session, 7)

    assert result.resolved_episodes == 1
    assert result.open_episodes == 0
    assert 71.9 <= result.mean_recovery_hours <= 72.1
    assert result.points[0].group == "Overall"


@pytest.mark.asyncio
async def test_recovery_excludes_open_episode_and_groups_by_module(db_session):
    session = db_session
    project, token = await _seed_context(session)
    checkout = await _case(session, "TC-CHECKOUT", "Checkout", PriorityLevel.CRITICAL)
    orders = await _case(session, "TC-ORDERS", "Orders", PriorityLevel.HIGH)
    await _result(session, project, token, checkout, days_ago=5, outcome=CaseStatus.failed)
    await _result(session, project, token, checkout, days_ago=4, outcome=CaseStatus.passed)
    await _result(session, project, token, orders, days_ago=3, outcome=CaseStatus.failed)
    await _result(session, project, token, orders, days_ago=2, outcome=CaseStatus.skipped)
    await session.commit()

    result = await get_recovery_trend(session, 7, "module")

    assert result.resolved_episodes == 1
    assert result.open_episodes == 1
    assert result.points[0].group == "Checkout"


@pytest.mark.asyncio
async def test_recovery_window_is_anchored_on_opening_failure(db_session):
    session = db_session
    project, token = await _seed_context(session)
    case = await _case(session, "TC-BOUNDARY", "Checkout", PriorityLevel.MEDIUM)
    await _result(session, project, token, case, days_ago=8, outcome=CaseStatus.failed)
    await _result(session, project, token, case, days_ago=1, outcome=CaseStatus.passed)
    await session.commit()

    result = await get_recovery_trend(session, 7)

    assert result.resolved_episodes == 0
    assert result.open_episodes == 0
    assert result.mean_recovery_hours is None


@pytest.mark.asyncio
async def test_recovery_groups_by_severity_and_keeps_identities_isolated(db_session):
    session = db_session
    project, token = await _seed_context(session)
    critical = await _case(session, "TC-CRIT", "Checkout", PriorityLevel.CRITICAL)
    low = await _case(session, "TC-LOW", "Search", PriorityLevel.LOW)
    await _result(session, project, token, critical, days_ago=5, outcome=CaseStatus.failed)
    await _result(session, project, token, low, days_ago=4, outcome=CaseStatus.passed)
    await _result(session, project, token, critical, days_ago=3, outcome=CaseStatus.passed)
    await session.commit()

    result = await get_recovery_trend(session, 7, "severity")

    assert result.resolved_episodes == 1
    assert result.points[0].group == "Critical"
    assert 47.9 <= result.mean_recovery_hours <= 48.1
