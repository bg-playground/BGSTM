from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from statistics import mean
from typing import Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.quality_metrics import (
    _VALID_WINDOWS,
    _load_case_rows,
    _load_requirement_context,
    _module_from_context,
    _severity_from_context,
    _window_start,
)
from app.models.external_case_result import CaseStatus, ExternalCaseResult
from app.models.test_case import TestCase
from app.schemas.quality_recovery import RecoveryTrendPoint, RecoveryTrendResponse

RecoveryGroupBy = Literal["overall", "module", "severity"]


def _stable_identity(case_result: ExternalCaseResult) -> str | None:
    if case_result.test_case_id is not None:
        return f"case:{case_result.test_case_id}"
    if case_result.external_id:
        return f"external:{case_result.external_id}"
    return None


async def get_recovery_trend(
    db: AsyncSession,
    window_days: int,
    group_by: RecoveryGroupBy = "overall",
) -> RecoveryTrendResponse:
    """Measure time-to-green from an opening failed execution to the next pass.

    The window is anchored on the opening failure. We intentionally load complete
    execution history so failures near the end of a reporting window can resolve
    later without inventing a defect-resolution timestamp.
    """

    if window_days not in _VALID_WINDOWS:
        raise ValueError(f"Unsupported window: {window_days}")
    if group_by not in {"overall", "module", "severity"}:
        raise ValueError(f"Unsupported recovery grouping: {group_by}")

    rows = await _load_case_rows(db)
    if not rows:
        return RecoveryTrendResponse(
            window_days=window_days,
            group_by=group_by,
            is_synthetic=True,
            reason="requires repeated external case-result outcomes; no execution results are available yet",
        )

    test_case_ids = [row.test_case_id for row, _test_case in rows if isinstance(row.test_case_id, UUID)]
    requirements_by_test_case_id = await _load_requirement_context(db, test_case_ids)
    start_at = _window_start(window_days)

    rows_by_identity: dict[str, list[tuple[ExternalCaseResult, TestCase | None]]] = defaultdict(list)
    for case_result, test_case in rows:
        identity = _stable_identity(case_result)
        if identity is not None:
            rows_by_identity[identity].append((case_result, test_case))

    resolved: list[tuple[datetime, str, str, float]] = []
    open_episodes = 0

    for identity_rows in rows_by_identity.values():
        ordered = sorted(identity_rows, key=lambda item: item[0].created_at)
        opening: tuple[ExternalCaseResult, TestCase | None] | None = None

        for case_result, test_case in ordered:
            if opening is None:
                if case_result.outcome == CaseStatus.failed and case_result.created_at >= start_at:
                    opening = (case_result, test_case)
                continue

            if case_result.outcome != CaseStatus.passed:
                continue

            failed_result, failed_test_case = opening
            test_case_id = failed_result.test_case_id if isinstance(failed_result.test_case_id, UUID) else None
            linked_requirements = requirements_by_test_case_id.get(test_case_id, []) if test_case_id else []
            module = _module_from_context(failed_test_case, linked_requirements)
            severity = _severity_from_context(failed_test_case, linked_requirements)
            duration_hours = (case_result.created_at - failed_result.created_at).total_seconds() / 3600
            resolved.append((failed_result.created_at, module, severity, duration_hours))
            opening = None

        if opening is not None:
            open_episodes += 1

    if not resolved:
        return RecoveryTrendResponse(
            window_days=window_days,
            group_by=group_by,
            mean_recovery_hours=None,
            resolved_episodes=0,
            open_episodes=open_episodes,
            is_synthetic=False,
            reason="No failed execution episode in the selected window has a subsequent passing execution yet.",
        )

    buckets: dict[tuple[datetime.date, str], list[float]] = defaultdict(list)
    for opened_at, module, severity, duration_hours in resolved:
        group = "Overall" if group_by == "overall" else (module if group_by == "module" else severity.title())
        buckets[(opened_at.date(), group)].append(duration_hours)

    points = [
        RecoveryTrendPoint(
            date=point_date,
            group=group,
            mean_recovery_hours=round(mean(durations), 2),
            resolved_episodes=len(durations),
        )
        for (point_date, group), durations in sorted(buckets.items(), key=lambda item: (item[0][0], item[0][1].lower()))
    ]

    return RecoveryTrendResponse(
        window_days=window_days,
        group_by=group_by,
        points=points,
        mean_recovery_hours=round(mean(item[3] for item in resolved), 2),
        resolved_episodes=len(resolved),
        open_episodes=open_episodes,
        is_synthetic=False,
    )
