"""AI Suggestion Engine Module

This module provides AI-powered link suggestion capabilities for BGSTM.
It analyzes requirements and test cases to automatically suggest potential links.
"""

from .config import SuggestionConfig
from .engine import SuggestionEngine

__all__ = ["SuggestionEngine", "SuggestionConfig"]
