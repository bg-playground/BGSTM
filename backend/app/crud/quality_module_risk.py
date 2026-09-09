from __future__ import annotations

from collections import defaultdict
from statistics import median
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.quality_metrics import (
    _VALID_WINDOWS,
    _load_case_rows,
    _load_requirement_context,
    _module_from_context,
    _window_start,
)
from app.models.external_case_result import CaseStatus
from app.models.link import LinkSource, RequirementTestCaseLink
from app.models.requirement import Requirement
from app.schemas.quality_module_risk import ModuleCoverageFailurePoint, ModuleCoverageFailureResponse

_ACCEPTED_LINK_SOURCES = {LinkSource.MANUAL, LinkSource.AI_CONFIRMED, LinkSource.IMPORTED}


def _requirement_module(requirement: Requirement) -> str:
    return str(requirement.module) if requirement.module else "Unassigned"


async def get_module_coverage_failure_density(
    db: AsyncSession,
    window_days: int,
) -> ModuleCoverageFailureResponse:
    """Combine traceability coverage with normalized execution failures by module."""

    if window_days not in _VALID_WINDOWS:
        raise ValueError(f"Unsupported window: {window_days}")

    requirements_result = await db.execute(select(Requirement).order_by(Requirement.created_at.asc()))
    requirements = list(requirements_result.scalars().all())
    if not requirements:
        return ModuleCoverageFailureResponse(
            points=[],
            is_synthetic=True,
            reason="requires requirements with module assignments; no requirements are available yet",
        )

    links_result = await db.execute(select(RequirementTestCaseLink.requirement_id, RequirementTestCaseLink.link_source))
    covered_requirement_ids = {
        requirement_id
        for requirement_id, link_source in links_result.all()
        if link_source in _ACCEPTED_LINK_SOURCES
    }

    requirement_buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "covered": 0})
    for requirement in requirements:
        module = _requirement_module(requirement)
        requirement_buckets[module]["total"] += 1
        if requirement.id in covered_requirement_ids:
            requirement_buckets[module]["covered"] += 1

    rows = await _load_case_rows(db, start_at=_window_start(window_days))
    test_case_ids = [row.test_case_id for row, _test_case in rows if isinstance(row.test_case_id, UUID)]
    requirements_by_test_case_id = await _load_requirement_context(db, test_case_ids)

    execution_buckets: dict[str, dict[str, int]] = defaultdict(lambda: {"executions": 0, "failures": 0})
    for case_result, test_case in rows:
        test_case_id = case_result.test_case_id if isinstance(case_result.test_case_id, UUID) else None
        linked_requirements = requirements_by_test_case_id.get(test_case_id, []) if test_case_id else []
        module = _module_from_context(test_case, linked_requirements)
        execution_buckets[module]["executions"] += 1
        if case_result.outcome == CaseStatus.failed:
            execution_buckets[module]["failures"] += 1

    points: list[ModuleCoverageFailurePoint] = []
    for module, requirement_counts in sorted(requirement_buckets.items(), key=lambda item: item[0].lower()):
        execution_counts = execution_buckets.get(module, {"executions": 0, "failures": 0})
        total_requirements = requirement_counts["total"]
        covered_requirements = requirement_counts["covered"]
        total_executions = execution_counts["executions"]
        total_failures = execution_counts["failures"]
        points.append(
            ModuleCoverageFailurePoint(
                module=module,
                coverage_pct=round(covered_requirements / total_requirements * 100, 2),
                failure_density_pct=round(total_failures / total_executions * 100, 2) if total_executions else 0.0,
                total_requirements=total_requirements,
                covered_requirements=covered_requirements,
                total_executions=total_executions,
                total_failures=total_failures,
            )
        )

    return ModuleCoverageFailureResponse(
        points=points,
        median_coverage_pct=round(float(median(point.coverage_pct for point in points)), 2),
        median_failure_density_pct=round(float(median(point.failure_density_pct for point in points)), 2),
        is_synthetic=False,
        reason=(
            "No execution results were recorded in the selected window; failure density is 0% until execution evidence exists."
            if not rows
            else None
        ),
    )
