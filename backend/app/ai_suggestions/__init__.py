"""AI Suggestion Engine Module

This module provides AI-powered link suggestion capabilities for BGSTM.
It analyzes requirements and test cases to automatically suggest potential links.
"""

from .engine import SuggestionEngine
from .config import SuggestionConfig

__all__ = ["SuggestionEngine", "SuggestionConfig"]
