"""API endpoints for Traceability Matrix and Metrics"""

import csv
import io
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.crud import traceability as crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.traceability import MetricsResponse, TraceabilityMatrixResponse

router = APIRouter()


@router.get("/traceability-matrix", response_model=TraceabilityMatrixResponse)
async def get_traceability_matrix(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the complete traceability matrix with coverage analysis.

    Returns:
        - Complete mapping of requirements to linked test cases
        - Coverage status per requirement (covered, partially covered, uncovered)
        - Overall coverage percentage
        - Orphan test cases (test cases with no linked requirements)
    """
    return await crud.get_traceability_matrix(db)


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get system metrics including coverage and suggestion acceptance rates.

    Returns:
        - Coverage percentage
        - Suggestion acceptance rate
        - Total counts for requirements, test cases, links, and suggestions
        - Breakdown by suggestion algorithm
        - Manual vs AI-suggested link counts
    """
    return await crud.get_metrics(db)


@router.get("/traceability-matrix/export")
async def export_traceability_matrix(
    format: Literal["csv", "json", "pdf"] = Query(..., description="Export format: csv, json, or pdf"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export the traceability matrix in CSV, JSON, or PDF format.

    Args:
        format: Export format (csv, json, or pdf)

    Returns:
        File download with appropriate content type
    """
    matrix_data = await crud.get_traceability_matrix(db)

    if format == "csv":
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "Requirement ID",
                "Requirement External ID",
                "Requirement Title",
                "Coverage Status",
                "Test Case ID",
                "Test Case Title",
                "Link Status",
                "Link Type",
                "Confidence Score",
            ]
        )

        # Write data rows
        for req_coverage in matrix_data.matrix:
            if req_coverage.linked_test_cases:
                for tc in req_coverage.linked_test_cases:
                    writer.writerow(
                        [
                            str(req_coverage.requirement_id),
                            req_coverage.external_id or "",
                            req_coverage.requirement_title,
                            req_coverage.coverage_status,
                            str(tc.test_case_id),
                            tc.title,
                            tc.link_status,
                            tc.link_type,
                            tc.confidence_score if tc.confidence_score is not None else "",
                        ]
                    )
            else:
                # Requirement with no links
                writer.writerow(
                    [
                        str(req_coverage.requirement_id),
                        req_coverage.external_id or "",
                        req_coverage.requirement_title,
                        req_coverage.coverage_status,
                        "",
                        "",
                        "",
                        "",
                        "",
                    ]
                )

        # Write orphan test cases section
        if matrix_data.orphans:
            writer.writerow([])  # Empty row separator
            writer.writerow(["Orphan Test Cases (No Linked Requirements)"])
            writer.writerow(["Test Case ID", "Test Case External ID", "Test Case Title"])
            for orphan in matrix_data.orphans:
                writer.writerow([str(orphan.test_case_id), orphan.external_id or "", orphan.title])

        csv_content = output.getvalue()
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=traceability_matrix.csv"},
        )

    elif format == "json":
        # Export as formatted JSON
        json_content = matrix_data.model_dump_json(indent=2)
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=traceability_matrix.json"},
        )

    elif format == "pdf":
        # Build PDF using reportlab
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75 * inch, bottomMargin=0.75 * inch)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph("BGSTM Traceability Matrix Report", styles["Title"]))
        gen_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        elements.append(Paragraph(f"Generated: {gen_date}", styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

        # Coverage Summary
        elements.append(Paragraph("Coverage Summary", styles["Heading2"]))
        summary_data = [
            ["Metric", "Value"],
            ["Total Requirements", str(matrix_data.total_requirements)],
            ["Covered Requirements", str(matrix_data.covered_requirements)],
            ["Uncovered Requirements", str(matrix_data.uncovered_requirements)],
            ["Coverage Percentage", f"{matrix_data.coverage_percentage:.1f}%"],
            ["Total Test Cases", str(matrix_data.total_test_cases)],
            ["Orphan Test Cases", str(matrix_data.orphan_test_cases)],
        ]
        summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Gap Analysis
        uncovered = [r for r in matrix_data.matrix if r.coverage_status == "uncovered"]
        elements.append(Paragraph("Gap Analysis – Uncovered Requirements", styles["Heading2"]))
        if uncovered:
            gap_data = [["External ID", "Requirement Title"]]
            for r in uncovered:
                gap_data.append([r.external_id or "", r.requirement_title])
            gap_table = Table(gap_data, colWidths=[1.5 * inch, 5 * inch])
            gap_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.red),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )
            elements.append(gap_table)
        else:
            elements.append(Paragraph("No uncovered requirements.", styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

        # Full Matrix Table
        elements.append(Paragraph("Requirements Coverage Matrix", styles["Heading2"]))
        matrix_table_data = [["Req ID", "Requirement Title", "Coverage", "Test Case Title", "Link Type", "Score"]]
        for req_coverage in matrix_data.matrix:
            if req_coverage.linked_test_cases:
                for i, tc in enumerate(req_coverage.linked_test_cases):
                    score = f"{tc.confidence_score:.2f}" if tc.confidence_score is not None else "—"
                    matrix_table_data.append(
                        [
                            req_coverage.external_id or "" if i == 0 else "",
                            req_coverage.requirement_title if i == 0 else "",
                            req_coverage.coverage_status.replace("_", " ").title() if i == 0 else "",
                            tc.title,
                            tc.link_type,
                            score,
                        ]
                    )
            else:
                matrix_table_data.append(
                    [
                        req_coverage.external_id or "",
                        req_coverage.requirement_title,
                        req_coverage.coverage_status.replace("_", " ").title(),
                        "—",
                        "—",
                        "—",
                    ]
                )
        col_widths = [1.0 * inch, 2.2 * inch, 1.1 * inch, 2.0 * inch, 0.8 * inch, 0.6 * inch]
        matrix_pdf_table = Table(matrix_table_data, colWidths=col_widths, repeatRows=1)
        matrix_pdf_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )
        elements.append(matrix_pdf_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Orphan Test Cases
        if matrix_data.orphans:
            elements.append(Paragraph("Orphan Test Cases (No Linked Requirements)", styles["Heading2"]))
            orphan_data = [["External ID", "Test Case Title"]]
            for orphan in matrix_data.orphans:
                orphan_data.append([orphan.external_id or "", orphan.title])
            orphan_table = Table(orphan_data, colWidths=[1.5 * inch, 5 * inch])
            orphan_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.orange),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )
            elements.append(orphan_table)

        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=traceability_matrix.pdf"},
        )
