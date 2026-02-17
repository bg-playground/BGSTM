"""Configuration for AI Suggestion Engine"""

from typing import Optional

from pydantic import BaseModel, Field


class SuggestionConfig(BaseModel):
    """Configuration for suggestion engine"""

    # Minimum confidence score threshold (0.0 to 1.0)
    min_confidence_threshold: float = Field(
        default=0.3, ge=0.0, le=1.0, description="Minimum confidence score to create a suggestion"
    )

    # Default algorithm to use
    default_algorithm: str = Field(
        default="tfidf", description="Default similarity algorithm: 'tfidf', 'keyword', or 'hybrid'"
    )

    # TF-IDF specific settings
    tfidf_max_features: Optional[int] = Field(
        default=100, description="Maximum number of features for TF-IDF vectorizer"
    )

    tfidf_ngram_range: tuple[int, int] = Field(default=(1, 2), description="N-gram range for TF-IDF (min, max)")

    # Keyword matching settings
    keyword_min_word_length: int = Field(default=3, description="Minimum word length for keyword extraction")

    keyword_top_n: int = Field(default=10, description="Number of top keywords to extract")

    # Hybrid approach weights
    hybrid_tfidf_weight: float = Field(
        default=0.6, ge=0.0, le=1.0, description="Weight for TF-IDF score in hybrid approach"
    )

    hybrid_keyword_weight: float = Field(
        default=0.4, ge=0.0, le=1.0, description="Weight for keyword score in hybrid approach"
    )

    # LLM embedding settings
    llm_provider: str = Field(default="openai", description="LLM provider: 'openai' or 'huggingface'")

    llm_model: Optional[str] = Field(
        default=None,
        description="Model name (defaults: 'text-embedding-3-small' for OpenAI, 'all-MiniLM-L6-v2' for HF)",
    )

    llm_cache_embeddings: bool = Field(default=True, description="Cache embeddings in memory for performance")

    class Config:
        frozen = False


# Default configuration instance
default_config = SuggestionConfig()
