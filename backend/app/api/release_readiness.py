import io
from datetime import timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.crud import release_readiness as crud
from app.db.session import get_db
from app.models.release_signoff import ReleaseSignoffRole
from app.models.user import User, UserRole
from app.schemas.release_readiness import ReadinessSnapshot, SignoffRequest

router = APIRouter(prefix="/release-readiness")


def _normalize_role(role: str) -> ReleaseSignoffRole:
    try:
        return ReleaseSignoffRole(role)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid sign-off role") from exc


def _enforce_signoff_permissions(role: ReleaseSignoffRole, current_user: User) -> None:
    if role in (ReleaseSignoffRole.qa_lead, ReleaseSignoffRole.eng_lead) and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required for qa_lead and eng_lead sign-off",
        )


def _build_markdown(snapshot: ReadinessSnapshot) -> str:
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
        "",
        "## Criteria",
        "",
        "| Category | Criterion | Status | Value | Threshold |",
        "|---|---|---|---|---|",
    ]

    for criterion in snapshot.criteria:
        row = (
            f"| {criterion.category} | {criterion.label} | {criterion.status} | "
            f"{criterion.value} | {criterion.threshold} |"
        )
        lines.append(row)

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
        row = (
            f"| {signoff.role} | {'yes' if signoff.signed_off else 'no'} | "
            f"{signoff.signed_off_by or ''} | {signed_at} | {signoff.note or ''} |"
        )
        lines.append(row)

    lines.append("")
    return "\n".join(lines)


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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    _ = current_user
    snapshot = await crud.get_readiness_snapshot(db)
    markdown_report = _build_markdown(snapshot)

    if format == "md":
        return Response(
            content=markdown_report,
            media_type="text/markdown",
            headers={"Content-Disposition": "attachment; filename=release_readiness_report.md"},
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Release Readiness Report", styles["Title"]), Spacer(1, 0.2 * inch)]

    elements.append(Paragraph(f"Overall Status: {snapshot.overall_status.upper()}", styles["Heading2"]))
    elements.append(Spacer(1, 0.1 * inch))

    summary_data = [
        ["Metric", "Value"],
        ["Passed", str(snapshot.summary.passed)],
        ["Warning", str(snapshot.summary.warning)],
        ["Failed", str(snapshot.summary.failed)],
        ["Total", str(snapshot.summary.total)],
    ]
    summary_table = Table(summary_data, colWidths=[2.5 * inch, 2.0 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Criteria", styles["Heading2"]))
    criteria_data = [["Category", "Criterion", "Status", "Value"]]
    for criterion in snapshot.criteria:
        criteria_data.append([criterion.category, criterion.label, criterion.status, criterion.value])

    criteria_table = Table(criteria_data, colWidths=[1.2 * inch, 3.0 * inch, 1.0 * inch, 1.4 * inch], repeatRows=1)
    criteria_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]
        )
    )
    elements.append(criteria_table)
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Sign-offs", styles["Heading2"]))
    signoff_data = [["Role", "Signed Off", "By", "At"]]
    for signoff in snapshot.signoffs:
        signoff_data.append(
            [
                signoff.role,
                "yes" if signoff.signed_off else "no",
                signoff.signed_off_by or "",
                (
                    signoff.signed_off_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
                    if signoff.signed_off_at
                    else ""
                ),
            ]
        )

    signoff_table = Table(signoff_data, colWidths=[1.2 * inch, 1.0 * inch, 2.0 * inch, 2.0 * inch], repeatRows=1)
    signoff_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]
        )
    )
    elements.append(signoff_table)

    doc.build(elements)
    pdf_content = buffer.getvalue()
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=release_readiness_report.pdf"},
    )
