import io
from dataclasses import dataclass
from datetime import timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.quality_metrics import WindowParam
from app.auth.dependencies import get_current_user
from app.crud import quality_metrics as quality_crud
from app.crud import release_readiness as crud
from app.crud.quality_recovery import get_recovery_trend
from app.db.session import get_db
from app.models.release_signoff import ReleaseSignoffRole
from app.models.user import User, UserRole
from app.schemas.quality_metrics import AutomationCoverageResponse, DefectsByModuleResponse
from app.schemas.quality_recovery import RecoveryTrendResponse
from app.schemas.release_readiness import ReadinessSnapshot, SignoffRequest

router = APIRouter(prefix="/release-readiness")


@dataclass(frozen=True)
class QualityKpiEvidence:
    window_days: int
    total_executions: int
    passed_executions: int
    pass_rate_pct: float | None
    pass_rate_reason: str | None
    failed_executions: int
    open_critical_failures: int
    automation: AutomationCoverageResponse
    recovery: RecoveryTrendResponse
    modules: DefectsByModuleResponse


def _normalize_role(role: str) -> ReleaseSignoffRole:
    try:
        return ReleaseSignoffRole(role)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid sign-off role",
        ) from exc


def _enforce_signoff_permissions(role: ReleaseSignoffRole, current_user: User) -> None:
    if role in (ReleaseSignoffRole.qa_lead, ReleaseSignoffRole.eng_lead) and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required for qa_lead and eng_lead sign-off",
        )


async def _get_quality_evidence(db: AsyncSession, window_days: int) -> QualityKpiEvidence:
    pass_rate = await quality_crud.get_pass_rate_trend(db, window_days)
    defect_trend = await quality_crud.get_defect_trend(db, window_days)
    modules = await quality_crud.get_defects_by_module(db, window_days, 5)
    automation = await quality_crud.get_automation_coverage(db)
    summary = await quality_crud.get_summary_stats(db)
    recovery = await get_recovery_trend(db, window_days, "overall")

    total_executions = sum(point.total_executed for point in pass_rate.points)
    passed_executions = sum(round(point.total_executed * point.pass_rate_pct / 100) for point in pass_rate.points)
    overall_pass_rate = round(passed_executions / total_executions * 100, 2) if total_executions else None

    return QualityKpiEvidence(
        window_days=window_days,
        total_executions=total_executions,
        passed_executions=passed_executions,
        pass_rate_pct=overall_pass_rate,
        pass_rate_reason=pass_rate.reason if total_executions == 0 else None,
        failed_executions=sum(point.total for point in defect_trend.points),
        open_critical_failures=summary.open_critical_defects,
        automation=automation,
        recovery=recovery,
        modules=modules,
    )


def _quality_markdown(evidence: QualityKpiEvidence) -> list[str]:
    lines = [
        "",
        f"## Quality KPI Evidence — Last {evidence.window_days} Days",
        "",
    ]
    if evidence.pass_rate_pct is None:
        reason = evidence.pass_rate_reason or "No executions are available."
        lines.append(f"- **Execution volume and pass rate:** {reason}")
    else:
        lines.append(
            f"- **Execution volume and pass rate:** {evidence.total_executions} executions; "
            f"{evidence.passed_executions} passed ({evidence.pass_rate_pct:.2f}%)."
        )

    lines.extend(
        [
            f"- **Failed executions in selected window:** {evidence.failed_executions}",
            (f"- **Open critical failures (current/latest state):** {evidence.open_critical_failures}"),
        ]
    )

    if evidence.automation.reason:
        lines.append(f"- **Automation coverage (current):** {evidence.automation.reason}")
    else:
        lines.append(
            "- **Automation coverage (current):** "
            f"{evidence.automation.percent_automated:.2f}% "
            f"({evidence.automation.automated}/{evidence.automation.total} "
            "test cases automated)."
        )

    if evidence.recovery.mean_recovery_hours is None:
        recovery_value = evidence.recovery.reason or "No resolved recovery episodes are available."
    else:
        recovery_value = f"{evidence.recovery.mean_recovery_hours:.2f} hours"

    lines.append(
        "- **Execution Mean Time to Recovery (time-to-green):** "
        f"{recovery_value}; {evidence.recovery.resolved_episodes} resolved episode(s), "
        f"{evidence.recovery.open_episodes} still open. "
        "This is execution recovery, not defect lifecycle Mean Time To Repair."
    )

    lines.extend(["", "### Top Failing Modules", ""])
    if evidence.modules.modules:
        lines.extend(f"- {bucket.module}: {bucket.count} failed execution(s)" for bucket in evidence.modules.modules)
    else:
        reason = evidence.modules.reason or "No failed executions were recorded in the selected window."
        lines.append(f"- {reason}")
    return lines


def _build_markdown(snapshot: ReadinessSnapshot, evidence: QualityKpiEvidence) -> str:
    generated_at = snapshot.generated_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Release Readiness Report",
        "",
        f"- **Overall status:** {snapshot.overall_status.upper()}",
        f"- **Generated at:** {generated_at}",
        "",
        "## Summary",
        "",
        f"- Passed: {snapshot.summary.passed}",
        f"- Warning: {snapshot.summary.warning}",
        f"- Failed: {snapshot.summary.failed}",
        f"- Total: {snapshot.summary.total}",
    ]
    lines.extend(_quality_markdown(evidence))
    lines.extend(
        [
            "",
            "## Criteria",
            "",
            "| Category | Criterion | Status | Value | Threshold |",
            "|---|---|---|---|---|",
        ]
    )
    for criterion in snapshot.criteria:
        lines.append(
            f"| {criterion.category} | {criterion.label} | {criterion.status} | "
            f"{criterion.value} | {criterion.threshold} |"
        )

    lines.extend(
        [
            "",
            "## Role Sign-offs",
            "",
            "| Role | Signed Off | Signed Off By | Signed Off At | Note |",
            "|---|---|---|---|---|",
        ]
    )
    for signoff in snapshot.signoffs:
        signed_at = (
            signoff.signed_off_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            if signoff.signed_off_at
            else ""
        )
        lines.append(
            f"| {signoff.role} | {'yes' if signoff.signed_off else 'no'} | "
            f"{signoff.signed_off_by or ''} | {signed_at} | {signoff.note or ''} |"
        )

    lines.append("")
    return "\n".join(lines)


def _table_style(header_color: colors.Color, font_size: int | None = None) -> TableStyle:
    commands: list[tuple[object, ...]] = [
        ("BACKGROUND", (0, 0), (-1, 0), header_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]
    if font_size is not None:
        commands.append(("FONTSIZE", (0, 0), (-1, -1), font_size))
    return TableStyle(commands)


@router.get("/", response_model=ReadinessSnapshot)
async def get_release_readiness(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReadinessSnapshot:
    _ = current_user
    return await crud.get_readiness_snapshot(db)


@router.post("/signoff", response_model=ReadinessSnapshot)
async def signoff_release_readiness(
    payload: SignoffRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReadinessSnapshot:
    role = _normalize_role(payload.role)
    _enforce_signoff_permissions(role, current_user)
    await crud.create_signoff(db, role, current_user.id, payload.note)
    return await crud.get_readiness_snapshot(db)


@router.delete("/signoff/{role}", response_model=ReadinessSnapshot)
async def revoke_release_signoff(
    role: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReadinessSnapshot:
    role_enum = _normalize_role(role)
    _enforce_signoff_permissions(role_enum, current_user)
    await crud.revoke_signoff(db, role_enum, current_user.id)
    return await crud.get_readiness_snapshot(db)


@router.post("/signoff/request", status_code=status.HTTP_204_NO_CONTENT)
async def request_release_signoff(
    payload: SignoffRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    role = _normalize_role(payload.role)
    await crud.request_signoff(db, role, current_user, payload.note)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/export")
async def export_release_readiness(
    format: Literal["md", "pdf"] = Query("md", description="Export format: md or pdf"),
    window: WindowParam = Query(WindowParam.DAYS_30),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    _ = current_user
    snapshot = await crud.get_readiness_snapshot(db)
    evidence = await _get_quality_evidence(db, int(window))
    markdown_report = _build_markdown(snapshot, evidence)

    if format == "md":
        return Response(
            content=markdown_report,
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment; filename=release_readiness_report.md"},
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("Release Readiness Report", styles["Title"]),
        Spacer(1, 0.2 * inch),
        Paragraph(
            f"Overall Status: {snapshot.overall_status.upper()}",
            styles["Heading2"],
        ),
        Spacer(1, 0.1 * inch),
    ]

    summary_data = [
        ["Metric", "Value"],
        ["Passed", str(snapshot.summary.passed)],
        ["Warning", str(snapshot.summary.warning)],
        ["Failed", str(snapshot.summary.failed)],
        ["Total", str(snapshot.summary.total)],
    ]
    summary_table = Table(summary_data, colWidths=[2.5 * inch, 2.0 * inch])
    summary_table.setStyle(_table_style(colors.darkblue))
    elements.extend(
        [
            summary_table,
            Spacer(1, 0.2 * inch),
            Paragraph(
                f"Quality KPI Evidence — Last {int(window)} Days",
                styles["Heading2"],
            ),
        ]
    )

    for line in _quality_markdown(evidence)[2:]:
        if line.startswith("### "):
            elements.append(Paragraph(line[4:], styles["Heading3"]))
        elif line.startswith("- "):
            elements.append(Paragraph(line[2:].replace("**", ""), styles["BodyText"]))

    elements.extend(
        [
            Spacer(1, 0.2 * inch),
            Paragraph("Criteria", styles["Heading2"]),
        ]
    )
    criteria_data = [["Category", "Criterion", "Status", "Value"]]
    criteria_data.extend(
        [criterion.category, criterion.label, criterion.status, criterion.value] for criterion in snapshot.criteria
    )
    criteria_table = Table(
        criteria_data,
        colWidths=[1.2 * inch, 3.0 * inch, 1.0 * inch, 1.4 * inch],
        repeatRows=1,
    )
    criteria_table.setStyle(_table_style(colors.grey, font_size=8))
    elements.extend(
        [
            criteria_table,
            Spacer(1, 0.2 * inch),
            Paragraph("Sign-offs", styles["Heading2"]),
        ]
    )

    signoff_data = [["Role", "Signed Off", "By", "At"]]
    for signoff in snapshot.signoffs:
        signed_at = (
            signoff.signed_off_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            if signoff.signed_off_at
            else ""
        )
        signoff_data.append(
            [
                signoff.role,
                "yes" if signoff.signed_off else "no",
                signoff.signed_off_by or "",
                signed_at,
            ]
        )

    signoff_table = Table(
        signoff_data,
        colWidths=[1.2 * inch, 1.0 * inch, 2.0 * inch, 2.0 * inch],
        repeatRows=1,
    )
    signoff_table.setStyle(_table_style(colors.grey, font_size=8))
    elements.append(signoff_table)

    doc.build(elements)
    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=release_readiness_report.pdf"},
    )
