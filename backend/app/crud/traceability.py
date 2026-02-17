"""CRUD operations for traceability matrix and metrics"""

from typing import Dict, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.link import LinkSource, RequirementTestCaseLink
from app.models.requirement import Requirement
from app.models.suggestion import LinkSuggestion, SuggestionStatus, SuggestionMethod
from app.models.test_case import TestCase
from app.schemas.traceability import (
    AlgorithmMetrics,
    LinkedTestCase,
    MetricsResponse,
    OrphanTestCase,
    RequirementCoverage,
    TraceabilityMatrixResponse,
)


async def get_traceability_matrix(db: AsyncSession) -> TraceabilityMatrixResponse:
    """
    Generate the complete traceability matrix with coverage analysis.

    Returns:
        TraceabilityMatrixResponse with requirements, links, coverage status, and orphans
    """
    # Get all requirements with their links
    query = select(Requirement).options(
        selectinload(Requirement.links).selectinload(RequirementTestCaseLink.test_case)
    )
    result = await db.execute(query)
    requirements = result.scalars().all()

    # Get all test cases to identify orphans
    test_case_query = select(TestCase).options(selectinload(TestCase.links))
    tc_result = await db.execute(test_case_query)
    test_cases = tc_result.scalars().all()

    # Build matrix data
    matrix = []
    covered_count = 0
    linked_test_case_ids = set()

    for req in requirements:
        # Filter accepted links
        accepted_links = [
            link
            for link in req.links
            if link.link_source in [LinkSource.MANUAL, LinkSource.AI_CONFIRMED, LinkSource.IMPORTED]
        ]

        # Build linked test cases
        linked_tcs = []
        for link in req.links:
            linked_test_case_ids.add(link.test_case_id)
            # Determine link status based on source
            if link.link_source == LinkSource.MANUAL:
                status = "accepted"
            elif link.link_source in [LinkSource.AI_CONFIRMED, LinkSource.IMPORTED]:
                status = "accepted"
            elif link.link_source == LinkSource.AI_SUGGESTED:
                status = "pending"
            else:
                status = "unknown"

            linked_tcs.append(
                LinkedTestCase(
                    test_case_id=link.test_case_id,
                    title=link.test_case.title,
                    link_status=status,
                    link_id=link.id,
                    link_type=link.link_type.value,
                    confidence_score=link.confidence_score,
                )
            )

        # Determine coverage status
        if len(accepted_links) > 0:
            coverage_status = "covered"
            covered_count += 1
        elif len(req.links) > 0:
            coverage_status = "partially_covered"
        else:
            coverage_status = "uncovered"

        matrix.append(
            RequirementCoverage(
                requirement_id=req.id,
                requirement_title=req.title,
                external_id=req.external_id,
                linked_test_cases=linked_tcs,
                coverage_status=coverage_status,
            )
        )

    # Find orphan test cases (no links)
    orphans = []
    for tc in test_cases:
        if tc.id not in linked_test_case_ids:
            orphans.append(OrphanTestCase(test_case_id=tc.id, title=tc.title, external_id=tc.external_id))

    # Calculate metrics
    total_requirements = len(requirements)
    uncovered_count = total_requirements - covered_count
    coverage_percentage = (covered_count / total_requirements * 100) if total_requirements > 0 else 0.0

    return TraceabilityMatrixResponse(
        coverage_percentage=round(coverage_percentage, 2),
        total_requirements=total_requirements,
        covered_requirements=covered_count,
        uncovered_requirements=uncovered_count,
        total_test_cases=len(test_cases),
        orphan_test_cases=len(orphans),
        matrix=matrix,
        orphans=orphans,
    )


async def get_metrics(db: AsyncSession) -> MetricsResponse:
    """
    Generate system metrics including coverage and suggestion acceptance rates.

    Returns:
        MetricsResponse with all key metrics and algorithm breakdown
    """
    # Count requirements
    req_count_query = select(func.count()).select_from(Requirement)
    req_result = await db.execute(req_count_query)
    total_requirements = req_result.scalar() or 0

    # Count test cases
    tc_count_query = select(func.count()).select_from(TestCase)
    tc_result = await db.execute(tc_count_query)
    total_test_cases = tc_result.scalar() or 0

    # Count total links
    link_count_query = select(func.count()).select_from(RequirementTestCaseLink)
    link_result = await db.execute(link_count_query)
    total_links = link_result.scalar() or 0

    # Count manual vs AI-suggested links
    manual_query = (
        select(func.count())
        .select_from(RequirementTestCaseLink)
        .where(RequirementTestCaseLink.link_source == LinkSource.MANUAL)
    )
    manual_result = await db.execute(manual_query)
    manual_links = manual_result.scalar() or 0

    ai_query = (
        select(func.count())
        .select_from(RequirementTestCaseLink)
        .where(RequirementTestCaseLink.link_source.in_([LinkSource.AI_CONFIRMED, LinkSource.AI_SUGGESTED]))
    )
    ai_result = await db.execute(ai_query)
    ai_suggested_links = ai_result.scalar() or 0

    # Get suggestions statistics
    sugg_count_query = select(func.count()).select_from(LinkSuggestion)
    sugg_result = await db.execute(sugg_count_query)
    total_suggestions = sugg_result.scalar() or 0

    accepted_query = (
        select(func.count())
        .select_from(LinkSuggestion)
        .where(LinkSuggestion.status == SuggestionStatus.ACCEPTED)
    )
    accepted_result = await db.execute(accepted_query)
    accepted_suggestions = accepted_result.scalar() or 0

    rejected_query = (
        select(func.count())
        .select_from(LinkSuggestion)
        .where(LinkSuggestion.status == SuggestionStatus.REJECTED)
    )
    rejected_result = await db.execute(rejected_query)
    rejected_suggestions = rejected_result.scalar() or 0

    pending_query = (
        select(func.count())
        .select_from(LinkSuggestion)
        .where(LinkSuggestion.status == SuggestionStatus.PENDING)
    )
    pending_result = await db.execute(pending_query)
    pending_suggestions = pending_result.scalar() or 0

    # Calculate acceptance rate
    suggestion_acceptance_rate = (
        (accepted_suggestions / total_suggestions * 100) if total_suggestions > 0 else 0.0
    )

    # Get requirements with at least one accepted link for coverage
    covered_reqs_query = (
        select(func.count(func.distinct(RequirementTestCaseLink.requirement_id)))
        .select_from(RequirementTestCaseLink)
        .where(RequirementTestCaseLink.link_source.in_([LinkSource.MANUAL, LinkSource.AI_CONFIRMED, LinkSource.IMPORTED]))
    )
    covered_result = await db.execute(covered_reqs_query)
    covered_requirements = covered_result.scalar() or 0

    coverage_percentage = (covered_requirements / total_requirements * 100) if total_requirements > 0 else 0.0

    # Algorithm breakdown
    algorithm_breakdown = []
    for method in SuggestionMethod:
        # Total for this method
        method_total_query = (
            select(func.count())
            .select_from(LinkSuggestion)
            .where(LinkSuggestion.suggestion_method == method)
        )
        method_total_result = await db.execute(method_total_query)
        method_total = method_total_result.scalar() or 0

        # Accepted for this method
        method_accepted_query = (
            select(func.count())
            .select_from(LinkSuggestion)
            .where(LinkSuggestion.suggestion_method == method, LinkSuggestion.status == SuggestionStatus.ACCEPTED)
        )
        method_accepted_result = await db.execute(method_accepted_query)
        method_accepted = method_accepted_result.scalar() or 0

        # Rejected for this method
        method_rejected_query = (
            select(func.count())
            .select_from(LinkSuggestion)
            .where(LinkSuggestion.suggestion_method == method, LinkSuggestion.status == SuggestionStatus.REJECTED)
        )
        method_rejected_result = await db.execute(method_rejected_query)
        method_rejected = method_rejected_result.scalar() or 0

        # Pending for this method
        method_pending_query = (
            select(func.count())
            .select_from(LinkSuggestion)
            .where(LinkSuggestion.suggestion_method == method, LinkSuggestion.status == SuggestionStatus.PENDING)
        )
        method_pending_result = await db.execute(method_pending_query)
        method_pending = method_pending_result.scalar() or 0

        method_acceptance_rate = (method_accepted / method_total * 100) if method_total > 0 else 0.0

        algorithm_breakdown.append(
            AlgorithmMetrics(
                algorithm=method.value,
                total_suggestions=method_total,
                accepted_suggestions=method_accepted,
                rejected_suggestions=method_rejected,
                pending_suggestions=method_pending,
                acceptance_rate=round(method_acceptance_rate, 2),
            )
        )

    return MetricsResponse(
        coverage_percentage=round(coverage_percentage, 2),
        suggestion_acceptance_rate=round(suggestion_acceptance_rate, 2),
        total_requirements=total_requirements,
        total_test_cases=total_test_cases,
        total_links=total_links,
        total_suggestions=total_suggestions,
        accepted_suggestions=accepted_suggestions,
        rejected_suggestions=rejected_suggestions,
        pending_suggestions=pending_suggestions,
        manual_links=manual_links,
        ai_suggested_links=ai_suggested_links,
        algorithm_breakdown=algorithm_breakdown,
    )
