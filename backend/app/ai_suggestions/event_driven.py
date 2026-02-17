"""Event-Driven Suggestion Generation Service

This module provides background task functions for automatic suggestion generation
when requirements or test cases are created or updated.
"""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai_suggestions.config import SuggestionConfig
from app.ai_suggestions.engine import SuggestionEngine
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_suggestions_for_requirement(
    requirement_id: UUID,
    db: AsyncSession,
    algorithm: Optional[str] = None,
    threshold: Optional[float] = None,
) -> None:
    """
    Generate suggestions for a specific requirement against all test cases.

    This function is designed to be run as a background task.

    Args:
        requirement_id: ID of the requirement to generate suggestions for
        db: Database session
        algorithm: Optional algorithm override. Uses settings if not provided.
        threshold: Optional threshold override. Uses settings if not provided.
    """
    try:
        logger.info(f"Starting auto-suggestion generation for requirement {requirement_id}")

        # Create config with overrides from settings or parameters
        config = SuggestionConfig(
            default_algorithm=algorithm or settings.AUTO_SUGGESTIONS_ALGORITHM,
            min_confidence_threshold=threshold or settings.AUTO_SUGGESTIONS_THRESHOLD,
        )

        # Initialize engine
        engine = SuggestionEngine(config=config)

        # Generate suggestions for this specific requirement
        result = await engine.generate_suggestions(
            db,
            requirement_ids=[requirement_id],
            test_case_ids=None,  # All test cases
        )

        logger.info(
            f"Auto-suggestion completed for requirement {requirement_id}: "
            f"{result['suggestions_created']} created, {result['suggestions_skipped']} skipped"
        )

    except Exception as e:
        logger.error(f"Error generating suggestions for requirement {requirement_id}: {str(e)}")


async def generate_suggestions_for_test_case(
    test_case_id: UUID,
    db: AsyncSession,
    algorithm: Optional[str] = None,
    threshold: Optional[float] = None,
) -> None:
    """
    Generate suggestions for a specific test case against all requirements.

    This function is designed to be run as a background task.

    Args:
        test_case_id: ID of the test case to generate suggestions for
        db: Database session
        algorithm: Optional algorithm override. Uses settings if not provided.
        threshold: Optional threshold override. Uses settings if not provided.
    """
    try:
        logger.info(f"Starting auto-suggestion generation for test case {test_case_id}")

        # Create config with overrides from settings or parameters
        config = SuggestionConfig(
            default_algorithm=algorithm or settings.AUTO_SUGGESTIONS_ALGORITHM,
            min_confidence_threshold=threshold or settings.AUTO_SUGGESTIONS_THRESHOLD,
        )

        # Initialize engine
        engine = SuggestionEngine(config=config)

        # Generate suggestions for this specific test case
        result = await engine.generate_suggestions(
            db,
            requirement_ids=None,  # All requirements
            test_case_ids=[test_case_id],
        )

        logger.info(
            f"Auto-suggestion completed for test case {test_case_id}: "
            f"{result['suggestions_created']} created, {result['suggestions_skipped']} skipped"
        )

    except Exception as e:
        logger.error(f"Error generating suggestions for test case {test_case_id}: {str(e)}")
