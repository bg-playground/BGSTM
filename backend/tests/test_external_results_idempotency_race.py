"""Regression coverage for session-scoped external-result idempotency (BGSTM#400)."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Importing app.main registers the complete model graph before Base.metadata.create_all.
from app import main as _main  # noqa: F401
from app.crud import external_case_results as crud
from app.models.base import Base
from app.models.external_case_result import ExternalCaseResult
from app.models.external_results import ExternalRunSession
from app.schemas.external_results import CaseOutcome, CaseResultCreate


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    await engine.dispose()


def _payload(*, session_id: uuid.UUID, external_id: str) -> CaseResultCreate:
    return CaseResultCreate(
        session_id=session_id,
        external_id=external_id,
        title="idempotency regression",
        outcome=CaseOutcome.passed,
        duration_ms=10,
        requirement_ids=[],
    )


@pytest.mark.asyncio
async def test_same_external_id_is_allowed_in_different_sessions(db_session: AsyncSession):
    project_id = uuid.uuid4()
    runner_token_id = uuid.uuid4()
    session_a = ExternalRunSession(
        id=uuid.uuid4(),
        project_id=project_id,
        runner="pytest",
        created_by_runner_token_id=runner_token_id,
    )
    session_b = ExternalRunSession(
        id=uuid.uuid4(),
        project_id=project_id,
        runner="pytest",
        created_by_runner_token_id=runner_token_id,
    )
    db_session.add_all([session_a, session_b])
    await db_session.commit()

    external_id = f"shared-{uuid.uuid4()}"
    first, first_created = await crud.create_case_result(
        db_session,
        session_id=session_a.id,
        payload=_payload(session_id=session_a.id, external_id=external_id),
        runner_token_id=runner_token_id,
    )
    second, second_created = await crud.create_case_result(
        db_session,
        session_id=session_b.id,
        payload=_payload(session_id=session_b.id, external_id=external_id),
        runner_token_id=runner_token_id,
    )

    assert first_created is True
    assert second_created is True
    assert first.id != second.id
    assert first.session_id == session_a.id
    assert second.session_id == session_b.id

    count_result = await db_session.execute(
        select(func.count()).select_from(ExternalCaseResult).where(ExternalCaseResult.external_id == external_id)
    )
    assert count_result.scalar_one() == 2


@pytest.mark.asyncio
async def test_sequential_same_session_duplicate_still_collapses(db_session: AsyncSession):
    runner_token_id = uuid.uuid4()
    session = ExternalRunSession(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        runner="pytest",
        created_by_runner_token_id=runner_token_id,
    )
    db_session.add(session)
    await db_session.commit()

    external_id = f"same-session-{uuid.uuid4()}"
    payload = _payload(session_id=session.id, external_id=external_id)
    first, first_created = await crud.create_case_result(
        db_session,
        session_id=session.id,
        payload=payload,
        runner_token_id=runner_token_id,
    )
    second, second_created = await crud.create_case_result(
        db_session,
        session_id=session.id,
        payload=payload,
        runner_token_id=runner_token_id,
    )

    assert first_created is True
    assert second_created is False
    assert first.id == second.id


@pytest.mark.asyncio
async def test_expected_case_result_uniqueness_race_recovers_existing_row(monkeypatch):
    session_id = uuid.uuid4()
    runner_token_id = uuid.uuid4()
    external_id = f"race-{uuid.uuid4()}"
    payload = _payload(session_id=session_id, external_id=external_id)

    existing = SimpleNamespace(
        id=uuid.uuid4(),
        session_id=session_id,
        test_case_id=uuid.uuid4(),
        external_id=external_id,
    )
    session = SimpleNamespace(id=session_id, project_id=uuid.uuid4())
    test_case = SimpleNamespace(id=existing.test_case_id)

    find_existing = AsyncMock(side_effect=[None, existing])
    hydrate = AsyncMock(return_value=existing)
    resolve_test_case = AsyncMock(return_value=(test_case, False))
    monkeypatch.setattr(crud, "_find_case_result_by_idempotency_key", find_existing)
    monkeypatch.setattr(crud, "_hydrate_idempotent_result", hydrate)
    monkeypatch.setattr(crud, "_resolve_or_create_test_case", resolve_test_case)

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = session
    db = MagicMock(spec=AsyncSession)
    db.execute = AsyncMock(return_value=execute_result)
    db.flush = AsyncMock(
        side_effect=IntegrityError(
            "INSERT",
            {},
            Exception("UNIQUE constraint failed: external_case_results.session_id, external_case_results.external_id"),
        )
    )
    db.rollback = AsyncMock()
    db.add = MagicMock()

    result, created = await crud.create_case_result(
        db,
        session_id=session_id,
        payload=payload,
        runner_token_id=runner_token_id,
    )

    assert result is existing
    assert created is False
    db.rollback.assert_awaited_once()
    assert find_existing.await_count == 2
    hydrate.assert_awaited_once()


@pytest.mark.asyncio
async def test_unrelated_integrity_error_is_not_masked(monkeypatch):
    session_id = uuid.uuid4()
    runner_token_id = uuid.uuid4()
    external_id = f"unrelated-{uuid.uuid4()}"
    payload = _payload(session_id=session_id, external_id=external_id)

    session = SimpleNamespace(id=session_id, project_id=uuid.uuid4())
    test_case = SimpleNamespace(id=uuid.uuid4())
    monkeypatch.setattr(crud, "_find_case_result_by_idempotency_key", AsyncMock(return_value=None))
    monkeypatch.setattr(crud, "_resolve_or_create_test_case", AsyncMock(return_value=(test_case, False)))

    execute_result = MagicMock()
    execute_result.scalar_one_or_none.return_value = session
    unrelated = IntegrityError("INSERT", {}, Exception("UNIQUE constraint failed: requirements.external_id"))
    db = MagicMock(spec=AsyncSession)
    db.execute = AsyncMock(return_value=execute_result)
    db.flush = AsyncMock(side_effect=unrelated)
    db.rollback = AsyncMock()
    db.add = MagicMock()

    with pytest.raises(IntegrityError) as exc_info:
        await crud.create_case_result(
            db,
            session_id=session_id,
            payload=payload,
            runner_token_id=runner_token_id,
        )

    assert exc_info.value is unrelated
    db.rollback.assert_not_awaited()
