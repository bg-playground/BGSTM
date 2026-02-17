"""Core Suggestion Engine"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.link import create_suggestion
from app.models.link import RequirementTestCaseLink
from app.models.requirement import Requirement
from app.models.suggestion import LinkSuggestion, SuggestionMethod, SuggestionStatus
from app.models.test_case import TestCase
from app.schemas.link import SuggestionCreate

from .algorithms import get_algorithm
from .config import SuggestionConfig, default_config


class SuggestionEngine:
    """
    AI-powered suggestion engine for requirement-test case links.

    This engine analyzes requirement and test case texts using various
    similarity algorithms to automatically suggest potential links.
    """

    def __init__(self, config: Optional[SuggestionConfig] = None):
        """
        Initialize the suggestion engine

        Args:
            config: Configuration object. Uses default if not provided.
        """
        self.config = config or default_config
        self.algorithm = get_algorithm(self.config.default_algorithm, self.config)

    def _combine_text(self, requirement: Requirement) -> str:
        """
        Combine requirement fields into a single text for analysis

        Args:
            requirement: Requirement model instance

        Returns:
            Combined text string
        """
        parts = [
            requirement.title or "",
            requirement.description or "",
        ]

        # Add module as context if available
        if requirement.module:
            parts.append(requirement.module)

        # Add tags as context if available
        if requirement.tags:
            parts.extend(requirement.tags)

        return " ".join(parts)

    def _combine_test_case_text(self, test_case: TestCase) -> str:
        """
        Combine test case fields into a single text for analysis

        Args:
            test_case: TestCase model instance

        Returns:
            Combined text string
        """
        parts = [
            test_case.title or "",
            test_case.description or "",
        ]

        # Add preconditions and postconditions
        if test_case.preconditions:
            parts.append(test_case.preconditions)

        if test_case.postconditions:
            parts.append(test_case.postconditions)

        # Add module as context if available
        if test_case.module:
            parts.append(test_case.module)

        # Add tags as context if available
        if test_case.tags:
            parts.extend(test_case.tags)

        # Add steps if available
        if test_case.steps:
            if isinstance(test_case.steps, list):
                parts.extend([str(step) for step in test_case.steps])
            elif isinstance(test_case.steps, dict):
                parts.extend([str(v) for v in test_case.steps.values()])

        return " ".join(parts)

    def compute_similarity(self, requirement: Requirement, test_case: TestCase) -> float:
        """
        Compute similarity score between a requirement and test case

        Args:
            requirement: Requirement model instance
            test_case: TestCase model instance

        Returns:
            Similarity score between 0.0 and 1.0
        """
        req_text = self._combine_text(requirement)
        tc_text = self._combine_test_case_text(test_case)

        return self.algorithm.compute_similarity(req_text, tc_text)

    async def _get_existing_links(self, db: AsyncSession) -> set[tuple[UUID, UUID]]:
        """
        Get all existing requirement-test case link pairs

        Args:
            db: Database session

        Returns:
            Set of (requirement_id, test_case_id) tuples
        """
        result = await db.execute(select(RequirementTestCaseLink))
        links = result.scalars().all()
        return {(link.requirement_id, link.test_case_id) for link in links}

    async def _get_existing_suggestions(self, db: AsyncSession) -> set[tuple[UUID, UUID]]:
        """
        Get all existing pending suggestion pairs

        Args:
            db: Database session

        Returns:
            Set of (requirement_id, test_case_id) tuples for pending suggestions
        """
        result = await db.execute(select(LinkSuggestion).where(LinkSuggestion.status == SuggestionStatus.PENDING))
        suggestions = result.scalars().all()
        return {(s.requirement_id, s.test_case_id) for s in suggestions}

    async def generate_suggestions(
        self, db: AsyncSession, requirement_ids: Optional[List[UUID]] = None, test_case_ids: Optional[List[UUID]] = None
    ) -> Dict[str, Any]:
        """
        Generate link suggestions for requirements and test cases

        Args:
            db: Database session
            requirement_ids: Optional list of specific requirement IDs to analyze
            test_case_ids: Optional list of specific test case IDs to analyze

        Returns:
            Dictionary with generation statistics:
            - pairs_analyzed: Number of requirement-test case pairs analyzed
            - suggestions_created: Number of new suggestions created
            - suggestions_skipped: Number of pairs skipped (existing link/suggestion or below threshold)
        """
        # Fetch requirements
        if requirement_ids:
            req_query = select(Requirement).where(Requirement.id.in_(requirement_ids))
        else:
            req_query = select(Requirement)

        req_result = await db.execute(req_query)
        requirements = list(req_result.scalars().all())

        # Fetch test cases
        if test_case_ids:
            tc_query = select(TestCase).where(TestCase.id.in_(test_case_ids))
        else:
            tc_query = select(TestCase)

        tc_result = await db.execute(tc_query)
        test_cases = list(tc_result.scalars().all())

        # Get existing links and suggestions to avoid duplicates
        existing_links = await self._get_existing_links(db)
        existing_suggestions = await self._get_existing_suggestions(db)

        pairs_analyzed = 0
        suggestions_created = 0
        suggestions_skipped = 0

        # Map algorithm name to SuggestionMethod enum
        method_map = {
            "tfidf": SuggestionMethod.SEMANTIC_SIMILARITY,
            "keyword": SuggestionMethod.KEYWORD_MATCH,
            "hybrid": SuggestionMethod.HYBRID,
        }
        suggestion_method = method_map.get(self.config.default_algorithm, SuggestionMethod.HEURISTIC)

        # Analyze all requirement-test case pairs
        for requirement in requirements:
            for test_case in test_cases:
                pairs_analyzed += 1

                # Skip if already linked
                if (requirement.id, test_case.id) in existing_links:
                    suggestions_skipped += 1
                    continue

                # Skip if suggestion already exists
                if (requirement.id, test_case.id) in existing_suggestions:
                    suggestions_skipped += 1
                    continue

                # Compute similarity
                similarity_score = self.compute_similarity(requirement, test_case)

                # Check threshold
                if similarity_score < self.config.min_confidence_threshold:
                    suggestions_skipped += 1
                    continue

                # Create suggestion
                suggestion_data = SuggestionCreate(
                    requirement_id=requirement.id,
                    test_case_id=test_case.id,
                    similarity_score=similarity_score,
                    suggestion_method=suggestion_method,
                    suggestion_reason=f"Similarity score: {similarity_score:.3f} using {self.config.default_algorithm}",
                    suggestion_metadata={
                        "algorithm": self.config.default_algorithm,
                        "threshold": self.config.min_confidence_threshold,
                    },
                )

                await create_suggestion(db, suggestion_data)
                suggestions_created += 1

        return {
            "pairs_analyzed": pairs_analyzed,
            "suggestions_created": suggestions_created,
            "suggestions_skipped": suggestions_skipped,
            "algorithm_used": self.config.default_algorithm,
            "threshold": self.config.min_confidence_threshold,
        }
