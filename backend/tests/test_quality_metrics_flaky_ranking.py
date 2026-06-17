from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.crud.quality_metrics import get_flaky_ranking
from app.models.base import Base
from app.models.external_case_result import CaseStatus, ExternalCaseResult
from app.models.external_results import ExternalRunSession, RunStatus
from app.models.project import Project
from app.models.requirement import PriorityLevel
from app.models.runner_token import RunnerToken
from app.models.test_case import TestCase, TestCaseStatus, TestCaseType
from app.models.user import User, UserRole


def _days_ago(days: int) -> datetime:
    return (datetime.now(timezone.utc) - timedelta(days=days)).replace(tzinfo=None)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


async def _seed_session(session: AsyncSession) -> tuple[uuid.UUID, uuid.UUID]:
    admin_user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        hashed_password="hashed",
        full_name="Admin User",
        role=UserRole.admin,
        is_active=True,
    )
    project = Project(id=uuid.uuid4(), name="ShopFlow", description="seed")
    session.add_all([admin_user, project])
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

    run_session = ExternalRunSession(
        id=uuid.uuid4(),
        project_id=project.id,
        runner="@bgstm/playwright-core@0.1.0",
        status=RunStatus.failed,
        git_sha="run-a",
        git_branch="main",
        ci_url="https://ci.example.com/runs/a",
        run_metadata={"os": "linux"},
        summary={"total": 10, "failed": 3},
        started_at=_days_ago(3),
        finished_at=_days_ago(3) + timedelta(minutes=5),
        created_by_runner_token_id=runner_token.id,
    )
    run_session_2 = ExternalRunSession(
        id=uuid.uuid4(),
        project_id=project.id,
        runner="@bgstm/playwright-core@0.1.0",
        status=RunStatus.failed,
        git_sha="run-b",
        git_branch="main",
        ci_url="https://ci.example.com/runs/b",
        run_metadata={"os": "linux"},
        summary={"total": 10, "failed": 2},
        started_at=_days_ago(2),
        finished_at=_days_ago(2) + timedelta(minutes=5),
        created_by_runner_token_id=runner_token.id,
    )
    session.add_all([run_session, run_session_2])
    await session.flush()
    return run_session.id, run_session_2.id


async def _add_case_result(
    session: AsyncSession,
    session_id: uuid.UUID,
    *,
    outcome: CaseStatus,
    created_at: datetime,
    test_case_id: uuid.UUID | None = None,
    external_id: str | None = None,
    title: str = "Case",
) -> None:
    session.add(
        ExternalCaseResult(
            id=uuid.uuid4(),
            session_id=session_id,
            test_case_id=test_case_id,
            external_id=external_id,
            title=title,
            outcome=outcome,
            duration_ms=1200,
            created_at=created_at,
            updated_at=created_at,
        )
    )


@pytest.mark.asyncio
async def test_flaky_ranking_empty_db_is_synthetic(db_session: AsyncSession) -> None:
    response = await get_flaky_ranking(db_session, 30)

    assert response.is_synthetic is True
    assert response.entries == []
    assert response.reason == "requires external case-result outcomes; no execution results are available yet"


@pytest.mark.asyncio
async def test_flaky_ranking_computes_flip_rates_and_limits_results(db_session: AsyncSession) -> None:
    run_session_id, run_session_id_2 = await _seed_session(db_session)
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    flip_case = TestCase(
        id=uuid.uuid4(),
        external_id="TC-FLIP",
        title="Flipping test",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.READY,
    )
    stable_case = TestCase(
        id=uuid.uuid4(),
        external_id="TC-STABLE",
        title="Stable test",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.READY,
    )
    single_run_case = TestCase(
        id=uuid.uuid4(),
        external_id="TC-ONE",
        title="Single run test",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.READY,
    )
    flaky_case = TestCase(
        id=uuid.uuid4(),
        external_id="TC-FLAKY",
        title="Runner-reported flaky test",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.READY,
    )
    boundary_case = TestCase(
        id=uuid.uuid4(),
        external_id="TC-BOUNDARY",
        title="Window boundary test",
        description="desc",
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.READY,
    )
    ext_only_identity = "EXT-ONLY"

    db_session.add_all([flip_case, stable_case, single_run_case, flaky_case, boundary_case])
    await db_session.flush()

    for offset_days, outcome in enumerate([CaseStatus.passed, CaseStatus.failed, CaseStatus.passed, CaseStatus.failed]):
        await _add_case_result(
            db_session,
            run_session_id,
            test_case_id=flip_case.id,
            external_id=f"FLIP-{offset_days}",
            outcome=outcome,
            created_at=now - timedelta(days=6 - offset_days),
            title=flip_case.title,
        )

    for offset_days in [3, 2, 1]:
        await _add_case_result(
            db_session,
            run_session_id,
            test_case_id=stable_case.id,
            external_id=f"STABLE-{offset_days}",
            outcome=CaseStatus.passed,
            created_at=now - timedelta(days=offset_days),
            title=stable_case.title,
        )

    await _add_case_result(
        db_session,
        run_session_id,
        test_case_id=single_run_case.id,
        external_id="ONE-0",
        outcome=CaseStatus.failed,
        created_at=now - timedelta(days=2),
        title=single_run_case.title,
    )

    for offset_days, outcome in enumerate([CaseStatus.passed, CaseStatus.flaky, CaseStatus.flaky]):
        await _add_case_result(
            db_session,
            run_session_id,
            test_case_id=flaky_case.id,
            external_id=f"FLAKY-{offset_days}",
            outcome=outcome,
            created_at=now - timedelta(days=4 - offset_days),
            title=flaky_case.title,
        )

    await _add_case_result(
        db_session,
        run_session_id,
        test_case_id=boundary_case.id,
        external_id="BOUNDARY-OUTSIDE",
        outcome=CaseStatus.failed,
        created_at=now - timedelta(days=31),
        title=boundary_case.title,
    )
    await _add_case_result(
        db_session,
        run_session_id,
        test_case_id=boundary_case.id,
        external_id="BOUNDARY-INSIDE",
        outcome=CaseStatus.passed,
        created_at=now - timedelta(days=1),
        title=boundary_case.title,
    )

    for offset_days, outcome in enumerate([CaseStatus.passed, CaseStatus.failed]):
        await _add_case_result(
            db_session,
            run_session_id if offset_days == 0 else run_session_id_2,
            test_case_id=None,
            external_id=ext_only_identity,
            outcome=outcome,
            created_at=now - timedelta(days=2 - offset_days),
            title="External identity only",
        )

    await db_session.commit()

    full_response = await get_flaky_ranking(db_session, 30, top_n=10)
    by_name = {entry.display_name: entry for entry in full_response.entries}

    assert full_response.is_synthetic is False
    assert full_response.reason is None
    assert by_name["Flipping test"].runs == 4
    assert by_name["Flipping test"].transitions == 3
    assert by_name["Flipping test"].flip_rate == pytest.approx(1.0)
    assert by_name["Runner-reported flaky test"].flaky_outcomes == 2
    assert by_name["Runner-reported flaky test"].transitions == 1
    assert by_name["Runner-reported flaky test"].flip_rate == pytest.approx(0.5)
    assert by_name[ext_only_identity].test_case_id is None
    assert by_name[ext_only_identity].external_id == ext_only_identity
    assert "Stable test" not in by_name
    assert "Single run test" not in by_name
    assert "Window boundary test" not in by_name

    capped_response = await get_flaky_ranking(db_session, 30, top_n=2)
    assert len(capped_response.entries) == 2
