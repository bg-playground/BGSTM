"""CRUD operations for External Case Results (BGSTM#303)."""

import uuid
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.external_case_result import CaseStatus, ExternalCaseResult
from app.models.external_results import ExternalRunSession
from app.models.link import LinkSource, LinkType, RequirementTestCaseLink
from app.models.requirement import PriorityLevel, Requirement, RequirementStatus, RequirementType
from app.models.test_case import TestCase, TestCaseStatus, TestCaseType
from app.schemas.external_results import CaseResultCreate, CaseResultUpdate


def _outcome_value(outcome: Any) -> str:
    return getattr(outcome, "value", str(outcome))


def _dedupe_requirement_ids(requirement_ids: list[UUID]) -> list[UUID]:
    seen_requirement_ids: set[UUID] = set()
    deduped_requirement_ids: list[UUID] = []

    for requirement_id in requirement_ids:
        if requirement_id in seen_requirement_ids:
            continue
        seen_requirement_ids.add(requirement_id)
        deduped_requirement_ids.append(requirement_id)

    return deduped_requirement_ids


def _dedupe_requirement_external_ids(requirement_external_ids: list[str]) -> list[str]:
    seen_external_ids: set[str] = set()
    deduped_external_ids: list[str] = []

    for external_id in requirement_external_ids:
        if external_id in seen_external_ids:
            continue
        seen_external_ids.add(external_id)
        deduped_external_ids.append(external_id)

    return deduped_external_ids


async def _get_requirement_ids_for_test_case(
    db: AsyncSession,
    *,
    test_case_id: UUID | None,
) -> list[UUID]:
    if test_case_id is None:
        return []

    result = await db.execute(
        select(RequirementTestCaseLink.requirement_id)
        .where(RequirementTestCaseLink.test_case_id == test_case_id)
        .order_by(RequirementTestCaseLink.created_at.asc())
    )
    return list(result.scalars().all())


async def _resolve_or_create_test_case(
    db: AsyncSession,
    *,
    project_id: UUID,
    payload: CaseResultCreate,
    runner_token_id: UUID,
) -> tuple[TestCase, bool]:
    if payload.test_case_id is not None:
        result = await db.execute(select(TestCase).where(TestCase.id == payload.test_case_id))
        test_case = result.scalar_one_or_none()
        if test_case is None:
            raise ValueError(
                {
                    "code": "case.test_case_not_found",
                    "message": f"Test case {payload.test_case_id} does not exist.",
                    "details": None,
                }
            )
        return test_case, False

    if payload.external_id is None:
        raise ValueError("external_id must be present when test_case_id is not provided")

    result = await db.execute(select(TestCase).where(TestCase.external_id == payload.external_id))
    test_case = result.scalar_one_or_none()
    if test_case is not None:
        return test_case, False

    test_case = TestCase(
        id=uuid.uuid4(),
        external_id=payload.external_id,
        title=payload.title,
        description=payload.title,
        type=TestCaseType.FUNCTIONAL,
        priority=PriorityLevel.MEDIUM,
        status=TestCaseStatus.DRAFT,
        auto_registered=True,
        created_by=f"runner_token:{runner_token_id}",
    )
    db.add(test_case)
    await db.flush()
    return test_case, True


async def _link_requirements(
    db: AsyncSession,
    *,
    test_case_id: UUID,
    requirement_ids: list[UUID],
) -> tuple[list[UUID], list[UUID]]:
    if not requirement_ids:
        return [], []

    deduped_ids = _dedupe_requirement_ids(requirement_ids)
    resolvable_ids, unresolved_ids = await _resolve_requirement_ids(db, requirement_ids=deduped_ids)

    values = [
        {
            "id": uuid.uuid4(),
            "requirement_id": requirement_id,
            "test_case_id": test_case_id,
            "link_type": LinkType.COVERS,
            "link_source": LinkSource.IMPORTED,
            "created_by": "external_results",
        }
        for requirement_id in resolvable_ids
    ]
    if values:
        if db.bind and db.bind.dialect.name == "postgresql":
            insert_stmt = postgresql_insert(RequirementTestCaseLink).values(values)
            stmt = insert_stmt.on_conflict_do_nothing(index_elements=["requirement_id", "test_case_id"])
        else:
            insert_stmt = sqlite_insert(RequirementTestCaseLink).values(values)
            stmt = insert_stmt.on_conflict_do_nothing(index_elements=["requirement_id", "test_case_id"])
        await db.execute(stmt)

    return await _get_requirement_ids_for_test_case(db, test_case_id=test_case_id), unresolved_ids


async def _resolve_requirement_ids(
    db: AsyncSession,
    *,
    requirement_ids: list[UUID],
) -> tuple[list[UUID], list[UUID]]:
    if not requirement_ids:
        return [], []

    requirement_rows = await db.execute(select(Requirement.id).where(Requirement.id.in_(requirement_ids)))
    known_requirement_ids = set(requirement_rows.scalars().all())
    resolvable_ids = [requirement_id for requirement_id in requirement_ids if requirement_id in known_requirement_ids]
    unresolved_ids = [
        requirement_id for requirement_id in requirement_ids if requirement_id not in known_requirement_ids
    ]
    return resolvable_ids, unresolved_ids


async def _resolve_requirement_external_ids(
    db: AsyncSession,
    *,
    requirement_external_ids: list[str] | None,
    auto_register_requirements: bool,
) -> tuple[list[UUID], list[str]]:
    if not requirement_external_ids:
        return [], []

    deduped_external_ids = _dedupe_requirement_external_ids(requirement_external_ids)
    requirement_rows = await db.execute(select(Requirement).where(Requirement.external_id.in_(deduped_external_ids)))
    requirements_by_external_id: dict[str, Requirement] = {}
    for requirement in requirement_rows.scalars().all():
        external_id = requirement.external_id
        if isinstance(external_id, str):
            requirements_by_external_id[external_id] = requirement

    resolved_ids: list[UUID] = []
    unresolved_ids: list[str] = []

    for submitted_external_id in deduped_external_ids:
        requirement = requirements_by_external_id.get(submitted_external_id)
        if requirement is not None:
            resolved_ids.append(requirement.id)
            continue

        if not auto_register_requirements:
            unresolved_ids.append(submitted_external_id)
            continue

        requirement = Requirement(
            external_id=submitted_external_id,
            title=submitted_external_id,
            description=f"Auto-registered from external ID {submitted_external_id}",
            type=RequirementType.FUNCTIONAL,
            priority=PriorityLevel.MEDIUM,
            status=RequirementStatus.DRAFT,
        )
        db.add(requirement)
        await db.flush()
        requirements_by_external_id[submitted_external_id] = requirement
        resolved_ids.append(requirement.id)

    return resolved_ids, unresolved_ids


async def create_case_result(
    db: AsyncSession,
    *,
    session_id: UUID,
    payload: CaseResultCreate,
    runner_token_id: UUID,
) -> tuple[ExternalCaseResult, bool]:
    if payload.external_id is not None:
        existing_result = await db.execute(
            select(ExternalCaseResult)
            .where(ExternalCaseResult.session_id == session_id)
            .where(ExternalCaseResult.external_id == payload.external_id)
        )
        existing = existing_result.scalar_one_or_none()
        if existing is not None:
            existing.requirement_ids = await _get_requirement_ids_for_test_case(db, test_case_id=existing.test_case_id)
            _resolvable_ids, unresolved_ids = await _resolve_requirement_ids(
                db,
                requirement_ids=payload.requirement_ids,
            )
            _resolved_external_ids, unresolved_external_ids = await _resolve_requirement_external_ids(
                db,
                requirement_external_ids=payload.requirement_external_ids,
                auto_register_requirements=False,
            )
            existing.unresolved_requirement_ids = unresolved_ids
            existing.unresolved_requirement_external_ids = unresolved_external_ids
            return existing, False

    session_result = await db.execute(select(ExternalRunSession).where(ExternalRunSession.id == session_id))
    session = session_result.scalar_one_or_none()
    if session is None:
        raise ValueError(
            {
                "code": "case.session_not_found",
                "message": f"Session {session_id} does not exist.",
                "details": None,
            }
        )

    test_case, was_auto_registered = await _resolve_or_create_test_case(
        db,
        project_id=session.project_id,
        payload=payload,
        runner_token_id=runner_token_id,
    )
    case_result = ExternalCaseResult(
        session_id=session_id,
        test_case_id=test_case.id,
        external_id=payload.external_id,
        title=payload.title,
        outcome=CaseStatus(payload.outcome.value),
        duration_ms=payload.duration_ms,
        error_message=payload.error_message,
        auto_registered=was_auto_registered,
    )
    db.add(case_result)
    await db.flush()
    resolvable_ids, unresolved_ids = await _resolve_requirement_ids(
        db,
        requirement_ids=payload.requirement_ids,
    )
    resolved_external_ids, unresolved_external_ids = await _resolve_requirement_external_ids(
        db,
        requirement_external_ids=payload.requirement_external_ids,
        auto_register_requirements=payload.auto_register_requirements,
    )
    linked_ids, _ = await _link_requirements(
        db,
        test_case_id=test_case.id,
        requirement_ids=_dedupe_requirement_ids(resolvable_ids + resolved_external_ids),
    )
    await db.commit()
    await db.refresh(case_result)
    case_result.requirement_ids = linked_ids
    case_result.unresolved_requirement_ids = unresolved_ids
    case_result.unresolved_requirement_external_ids = unresolved_external_ids
    return case_result, True


def _is_transition_allowed(current_status: str, requested_status: str) -> bool:
    if current_status == "started":
        return True
    if current_status in {"passed", "failed", "skipped"}:
        return requested_status == "flaky"
    if current_status == "flaky":
        return requested_status == "flaky"
    if current_status == "aborted":
        return False
    return False


async def update_case_result(
    db: AsyncSession,
    *,
    case_result_id: UUID,
    payload: CaseResultUpdate,
) -> ExternalCaseResult | None:
    result = await db.execute(select(ExternalCaseResult).where(ExternalCaseResult.id == case_result_id))
    case_result = result.scalar_one_or_none()
    if case_result is None:
        return None

    if payload.outcome is not None:
        current_status = _outcome_value(case_result.outcome)
        requested_status = payload.outcome.value
        if not _is_transition_allowed(current_status, requested_status):
            raise ValueError(
                {
                    "code": "case.transition.invalid",
                    "message": (
                        f"Cannot transition case result from '{current_status}' to '{requested_status}': "
                        "transition is not allowed."
                    ),
                    "details": {"current_status": current_status, "requested_status": requested_status},
                }
            )
        case_result.outcome = CaseStatus(requested_status)

    if payload.duration_ms is not None:
        case_result.duration_ms = payload.duration_ms

    if payload.error_message is not None:
        case_result.error_message = payload.error_message

    await db.commit()
    await db.refresh(case_result)
    case_result.requirement_ids = await _get_requirement_ids_for_test_case(db, test_case_id=case_result.test_case_id)
    return case_result


async def get_case_result(
    db: AsyncSession,
    case_result_id: UUID,
) -> ExternalCaseResult | None:
    result = await db.execute(select(ExternalCaseResult).where(ExternalCaseResult.id == case_result_id))
    case_result = result.scalar_one_or_none()
    if case_result is None:
        return None

    case_result.requirement_ids = await _get_requirement_ids_for_test_case(db, test_case_id=case_result.test_case_id)
    return case_result
