"""API endpoints for Traceability Matrix and Metrics"""

import csv
import io
import json
from typing import Literal

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import traceability as crud
from app.db.session import get_db
from app.schemas.traceability import MetricsResponse, TraceabilityMatrixResponse

router = APIRouter()


@router.get("/traceability-matrix", response_model=TraceabilityMatrixResponse)
async def get_traceability_matrix(db: AsyncSession = Depends(get_db)):
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
async def get_metrics(db: AsyncSession = Depends(get_db)):
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
    format: Literal["csv", "json"] = Query(..., description="Export format: csv or json"),
    db: AsyncSession = Depends(get_db),
):
    """
    Export the traceability matrix in CSV or JSON format.

    Args:
        format: Export format (csv or json)

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
