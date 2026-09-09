from __future__ import annotations

from collections import defaultdict
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.quality_metrics import (
    _load_case_rows,
    _load_requirement_context,
    _module_from_context,
    _window_start,
)
from app.models.external_case_result import CaseStatus, ExternalCaseResult
from app.models.test_case import TestCase
from app.schemas.quality_recurring import RecurringDefectEntry, RecurringDefectsParetoResponse

_VALID_WINDOWS = {7, 30, 90}


async def get_recurring_defects_pareto(
    db: AsyncSession,
    window_days: int,
    top_n: int = 10,
) -> RecurringDefectsParetoResponse:
    """Return repeated failed executions ranked by test identity.

    A recurring defect requires at least two failed executions for the same test
    identity inside the selected window. The stable identity is ``test_case_id``
    when available, falling back to ``external_id`` for unregistered results.
    Cumulative percentage is calculated across all recurring failures before the
    response is truncated to ``top_n``.
    """

    if window_days not in _VALID_WINDOWS:
        raise ValueError(f"Unsupported window: {window_days}")

    rows = await _load_case_rows(db, start_at=_window_start(window_days))
    if not rows:
        return RecurringDefectsParetoResponse(
            entries=[],
            total_recurring_failures=0,
            is_synthetic=True,
            reason="requires external case-result outcomes; no execution results are available yet",
        )

    failed_rows = [
        (case_result, test_case) for case_result, test_case in rows if case_result.outcome == CaseStatus.failed
    ]
    if not failed_rows:
        return RecurringDefectsParetoResponse(
            entries=[],
            total_recurring_failures=0,
            is_synthetic=False,
            reason="No failed execution results were recorded in the selected window.",
        )

    test_case_ids = [
        case_result.test_case_id
        for case_result, _test_case in failed_rows
        if isinstance(case_result.test_case_id, UUID)
    ]
    requirements_by_test_case_id = await _load_requirement_context(db, test_case_ids)

    grouped: dict[str, list[tuple[ExternalCaseResult, TestCase | None]]] = defaultdict(list)
    for case_result, test_case in failed_rows:
        identity = str(case_result.test_case_id or case_result.external_id or case_result.id)
        grouped[identity].append((case_result, test_case))

    recurring_groups = [identity_rows for identity_rows in grouped.values() if len(identity_rows) >= 2]
    if not recurring_groups:
        return RecurringDefectsParetoResponse(
            entries=[],
            total_recurring_failures=0,
            is_synthetic=False,
            reason="No test failed more than once in the selected window.",
        )

    ranked_groups = sorted(
        recurring_groups,
        key=lambda identity_rows: (
            -len(identity_rows),
            (
                identity_rows[-1][1].title
                if identity_rows[-1][1] and identity_rows[-1][1].title
                else identity_rows[-1][0].title
            ).lower(),
        ),
    )
    total_recurring_failures = sum(len(identity_rows) for identity_rows in ranked_groups)

    cumulative_failures = 0
    entries: list[RecurringDefectEntry] = []
    for identity_rows in ranked_groups:
        ordered_rows = sorted(identity_rows, key=lambda item: item[0].created_at)
        latest_result, latest_test_case = ordered_rows[-1]
        failure_count = len(ordered_rows)
        cumulative_failures += failure_count

        test_case_id = latest_result.test_case_id if isinstance(latest_result.test_case_id, UUID) else None
        linked_requirements = requirements_by_test_case_id.get(test_case_id, []) if test_case_id else []
        display_name = latest_test_case.title if latest_test_case and latest_test_case.title else latest_result.title

        entries.append(
            RecurringDefectEntry(
                test_case_id=test_case_id,
                external_id=latest_result.external_id,
                display_name=display_name,
                module=_module_from_context(latest_test_case, linked_requirements),
                failure_count=failure_count,
                cumulative_pct=round(cumulative_failures / total_recurring_failures * 100, 2),
                latest_failure_session_id=latest_result.session_id,
                latest_failure_at=latest_result.created_at,
            )
        )

    return RecurringDefectsParetoResponse(
        entries=entries[:top_n],
        total_recurring_failures=total_recurring_failures,
        is_synthetic=False,
    )
