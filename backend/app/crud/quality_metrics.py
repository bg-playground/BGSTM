from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.external_case_result import CaseStatus, ExternalCaseResult
from app.models.link import RequirementTestCaseLink
from app.models.requirement import PriorityLevel, Requirement
from app.models.test_case import AutomationStatus, TestCase
from app.schemas.quality_metrics import (
    AutomationCoverageResponse,
    DefectsByModuleResponse,
    DefectTrendPoint,
    DefectTrendResponse,
    ModuleQualityBucket,
    PassRateTrendPoint,
    PassRateTrendResponse,
    QualityDashboardSnapshot,
    SeverityMix,
    SummaryStatsResponse,
)

_VALID_WINDOWS = {7, 30, 90}


def _utc_today() -> date:
    return datetime.now(timezone.utc).date()


def _window_dates(window_days: int) -> list[date]:
    end_date = _utc_today()
    start_date = end_date - timedelta(days=window_days - 1)
    return [start_date + timedelta(days=offset) for offset in range(window_days)]


def _window_start(window_days: int) -> datetime:
    first_day = _window_dates(window_days)[0]
    return datetime.combine(first_day, time.min)


def _priority_value(value: Any) -> str | None:
    if value is None:
        return None
    return getattr(value, "value", str(value))


def _severity_from_context(test_case: TestCase | None, linked_requirements: list[Requirement]) -> str:
    priority_value = _priority_value(getattr(test_case, "priority", None))
    if priority_value in {"critical", "high", "medium", "low"}:
        return priority_value

    for requirement in linked_requirements:
        requirement_priority = _priority_value(getattr(requirement, "priority", None))
        if requirement_priority in {"critical", "high", "medium", "low"}:
            return requirement_priority

    return PriorityLevel.MEDIUM.value


def _module_from_context(test_case: TestCase | None, linked_requirements: list[Requirement]) -> str:
    """Derive a stable module label from the existing domain data.

    We prefer ``TestCase.module`` because it is the most explicit, existing field for
    execution-focused reporting. When that is empty we fall back to the first linked
    ``Requirement.module``, then the first test-case tag, and finally the external-id
    prefix so older or auto-registered records still land in a deterministic bucket.
    """

    if test_case is not None:
        if test_case.module:
            return str(test_case.module)
        if test_case.tags:
            first_tag = test_case.tags[0]
            if first_tag:
                return str(first_tag)
        if test_case.external_id and "-" in test_case.external_id:
            return test_case.external_id.split("-", 1)[0]
        if test_case.external_id:
            return str(test_case.external_id)

    for requirement in linked_requirements:
        if requirement.module:
            return str(requirement.module)

    return "Unassigned"


async def _load_requirement_context(
    db: AsyncSession,
    test_case_ids: list[UUID],
) -> dict[UUID, list[Requirement]]:
    if not test_case_ids:
        return {}

    result = await db.execute(
        select(RequirementTestCaseLink.test_case_id, Requirement)
        .join(Requirement, Requirement.id == RequirementTestCaseLink.requirement_id)
        .where(RequirementTestCaseLink.test_case_id.in_(test_case_ids))
        .order_by(RequirementTestCaseLink.created_at.asc())
    )

    requirements_by_test_case_id: dict[UUID, list[Requirement]] = defaultdict(list)
    for test_case_id, requirement in result.all():
        requirements_by_test_case_id[test_case_id].append(requirement)
    return requirements_by_test_case_id


async def _load_case_rows(
    db: AsyncSession,
    *,
    start_at: datetime | None = None,
) -> list[tuple[ExternalCaseResult, TestCase | None]]:
    query = (
        select(ExternalCaseResult, TestCase)
        .outerjoin(TestCase, ExternalCaseResult.test_case_id == TestCase.id)
        .order_by(ExternalCaseResult.created_at.asc())
    )
    if start_at is not None:
        query = query.where(ExternalCaseResult.created_at >= start_at)

    result = await db.execute(query)
    return list(result.all())


def _severity_mix() -> dict[str, int]:
    return {"critical": 0, "high": 0, "medium": 0, "low": 0}


def _to_severity_mix(values: dict[str, int]) -> SeverityMix:
    return SeverityMix(
        critical=values["critical"],
        high=values["high"],
        medium=values["medium"],
        low=values["low"],
    )


def _point_map(window_days: int) -> dict[date, dict[str, Any]]:
    return {
        point_date: {"total": 0, "by_severity": _severity_mix(), "pass_count": 0, "executed": 0}
        for point_date in _window_dates(window_days)
    }


async def get_defect_trend(db: AsyncSession, window_days: int) -> DefectTrendResponse:
    if window_days not in _VALID_WINDOWS:
        raise ValueError(f"Unsupported window: {window_days}")

    bucket_map = _point_map(window_days)
    rows = await _load_case_rows(db, start_at=_window_start(window_days))

    if not rows:
        return DefectTrendResponse(
            points=[DefectTrendPoint(date=point_date, total=0, by_severity=SeverityMix()) for point_date in bucket_map],
            is_synthetic=True,
            reason="requires external case-result outcomes; no execution results are available yet",
        )

    test_case_ids = [row.test_case_id for row, _test_case in rows if row.test_case_id is not None]
    requirements_by_test_case_id = await _load_requirement_context(db, test_case_ids)

    for case_result, test_case in rows:
        bucket_date = case_result.created_at.date()
        bucket = bucket_map.get(bucket_date)
        if bucket is None or case_result.outcome != CaseStatus.failed:
            continue

        test_case_id = case_result.test_case_id if isinstance(case_result.test_case_id, UUID) else None
        linked_requirements = requirements_by_test_case_id.get(test_case_id, []) if test_case_id else []
        severity = _severity_from_context(test_case, linked_requirements)
        bucket["total"] += 1
        bucket["by_severity"][severity] += 1

    return DefectTrendResponse(
        points=[
            DefectTrendPoint(
                date=point_date,
                total=bucket["total"],
                by_severity=_to_severity_mix(bucket["by_severity"]),
            )
            for point_date, bucket in bucket_map.items()
        ],
        is_synthetic=False,
    )


async def get_pass_rate_trend(db: AsyncSession, window_days: int) -> PassRateTrendResponse:
    if window_days not in _VALID_WINDOWS:
        raise ValueError(f"Unsupported window: {window_days}")

    bucket_map = _point_map(window_days)
    rows = await _load_case_rows(db, start_at=_window_start(window_days))

    if not rows:
        return PassRateTrendResponse(
            points=[
                PassRateTrendPoint(date=point_date, pass_rate_pct=0.0, total_executed=0) for point_date in bucket_map
            ],
            is_synthetic=True,
            reason="requires external case-result outcomes; no execution results are available yet",
        )

    for case_result, _test_case in rows:
        bucket = bucket_map.get(case_result.created_at.date())
        if bucket is None:
            continue
        bucket["executed"] += 1
        if case_result.outcome == CaseStatus.passed:
            bucket["pass_count"] += 1

    return PassRateTrendResponse(
        points=[
            PassRateTrendPoint(
                date=point_date,
                pass_rate_pct=round(
                    (bucket["pass_count"] / bucket["executed"] * 100) if bucket["executed"] else 0.0,
                    2,
                ),
                total_executed=bucket["executed"],
            )
            for point_date, bucket in bucket_map.items()
        ],
        is_synthetic=False,
    )


async def get_defects_by_module(
    db: AsyncSession,
    window_days: int,
    top_n: int = 10,
) -> DefectsByModuleResponse:
    if window_days not in _VALID_WINDOWS:
        raise ValueError(f"Unsupported window: {window_days}")

    rows = await _load_case_rows(db, start_at=_window_start(window_days))
    if not rows:
        return DefectsByModuleResponse(
            modules=[],
            is_synthetic=True,
            reason="requires external case-result outcomes; no execution results are available yet",
        )

    test_case_ids = [row.test_case_id for row, _test_case in rows if row.test_case_id is not None]
    requirements_by_test_case_id = await _load_requirement_context(db, test_case_ids)

    buckets: dict[str, dict[str, Any]] = {}
    for case_result, test_case in rows:
        if case_result.outcome != CaseStatus.failed:
            continue

        test_case_id = case_result.test_case_id if isinstance(case_result.test_case_id, UUID) else None
        linked_requirements = requirements_by_test_case_id.get(test_case_id, []) if test_case_id else []
        module_name = _module_from_context(test_case, linked_requirements)
        severity = _severity_from_context(test_case, linked_requirements)

        bucket = buckets.setdefault(module_name, {"count": 0, "severity_mix": _severity_mix()})
        bucket["count"] += 1
        bucket["severity_mix"][severity] += 1

    if not buckets:
        return DefectsByModuleResponse(
            modules=[],
            is_synthetic=False,
            reason="No failed execution results were recorded in the selected window.",
        )

    sorted_buckets = sorted(
        buckets.items(),
        key=lambda item: (-item[1]["count"], item[0].lower()),
    )[:top_n]

    return DefectsByModuleResponse(
        modules=[
            ModuleQualityBucket(
                module=module_name,
                count=data["count"],
                severity_mix=_to_severity_mix(data["severity_mix"]),
            )
            for module_name, data in sorted_buckets
        ],
        is_synthetic=False,
    )


async def get_automation_coverage(db: AsyncSession) -> AutomationCoverageResponse:
    result = await db.execute(select(TestCase.automation_status))
    statuses = list(result.scalars().all())

    automated = sum(1 for status in statuses if status == AutomationStatus.AUTOMATED)
    manual = sum(1 for status in statuses if status == AutomationStatus.MANUAL)
    in_progress = sum(1 for status in statuses if status == AutomationStatus.AUTOMATABLE)
    total = len(statuses)

    return AutomationCoverageResponse(
        total=total,
        automated=automated,
        manual=manual,
        in_progress=in_progress,
        percent_automated=round((automated / total * 100) if total else 0.0, 2),
        reason=None if total else "No test cases are available yet, so automation coverage is not populated.",
    )


async def get_summary_stats(db: AsyncSession) -> SummaryStatsResponse:
    rows_30d = await _load_case_rows(db, start_at=_window_start(30))
    total_defects_30d = sum(1 for case_result, _test_case in rows_30d if case_result.outcome == CaseStatus.failed)

    all_rows = await _load_case_rows(db)
    test_case_ids = [row.test_case_id for row, _test_case in all_rows if row.test_case_id is not None]
    requirements_by_test_case_id = await _load_requirement_context(db, test_case_ids)

    latest_by_identity: dict[str, tuple[ExternalCaseResult, TestCase | None]] = {}
    for case_result, test_case in all_rows:
        identity = str(case_result.test_case_id or case_result.external_id or case_result.id)
        current = latest_by_identity.get(identity)
        if current is None or case_result.created_at >= current[0].created_at:
            latest_by_identity[identity] = (case_result, test_case)

    open_critical_defects = 0
    for case_result, test_case in latest_by_identity.values():
        if case_result.outcome != CaseStatus.failed:
            continue
        test_case_id = case_result.test_case_id if isinstance(case_result.test_case_id, UUID) else None
        linked_requirements = requirements_by_test_case_id.get(test_case_id, []) if test_case_id else []
        if _severity_from_context(test_case, linked_requirements) == PriorityLevel.CRITICAL.value:
            open_critical_defects += 1

    return SummaryStatsResponse(
        defect_removal_efficiency_pct=None,
        defect_removal_efficiency_reason=(
            "requires a distinct post-release defect source to compare escaped defects with pre-release findings"
        ),
        mean_time_to_repair_hours=None,
        mean_time_to_repair_hours_reason=(
            "requires defect resolution timestamps that are not present in the current schema"
        ),
        escape_rate_pct=None,
        escape_rate_pct_reason=(
            "requires production or post-release defect records that are not present in the current schema"
        ),
        total_defects_30d=total_defects_30d,
        open_critical_defects=open_critical_defects,
    )


async def get_quality_dashboard_snapshot(db: AsyncSession, window_days: int = 30) -> QualityDashboardSnapshot:
    if window_days not in _VALID_WINDOWS:
        raise ValueError(f"Unsupported window: {window_days}")

    return QualityDashboardSnapshot(
        generated_at=datetime.now(timezone.utc),
        window_days=window_days,
        defect_trend=await get_defect_trend(db, window_days),
        pass_rate_trend=await get_pass_rate_trend(db, window_days),
        defects_by_module=await get_defects_by_module(db, window_days),
        automation_coverage=await get_automation_coverage(db),
        summary_stats=await get_summary_stats(db),
    )
