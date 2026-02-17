# AI Suggestions Module

This module provides AI-powered link suggestion capabilities for BGSTM. It analyzes requirements and test cases to automatically suggest potential traceability links based on text similarity.

## Overview

The AI suggestions engine computes similarity scores between requirements and test cases using various algorithms, then creates `LinkSuggestion` records for pairs that exceed a configurable confidence threshold. Users can review these suggestions and accept or reject them.

## Available Algorithms

### 1. TF-IDF + Cosine Similarity (`tfidf`)

**How it works:**
- Uses Term Frequency-Inverse Document Frequency (TF-IDF) to convert text into numerical vectors
- Computes cosine similarity between requirement and test case vectors
- Best for: Semantic similarity, finding documents that discuss similar topics even with different wording

**Requirements:**
- Requires `scikit-learn` library (included in requirements.txt)

**Pros:**
- Good at finding semantic similarity
- Handles synonyms and related concepts well
- Industry-standard approach

**Cons:**
- Requires external library
- Higher computational cost for large datasets

**Configuration:**
```python
config = SuggestionConfig(
    default_algorithm="tfidf",
    tfidf_max_features=100,      # Maximum vocabulary size
    tfidf_ngram_range=(1, 2)     # Consider 1-grams and 2-grams
)
```

### 2. Keyword Matching (`keyword`)

**How it works:**
- Extracts top N keywords from each text (after removing stop words)
- Computes Jaccard similarity (intersection over union) of keyword sets
- Best for: Direct keyword overlap, exact term matching

**Requirements:**
- No external dependencies (uses standard library only)

**Pros:**
- Fast and lightweight
- No external dependencies
- Interpretable results

**Cons:**
- Misses semantic similarity
- Sensitive to exact wording

**Configuration:**
```python
config = SuggestionConfig(
    default_algorithm="keyword",
    keyword_min_word_length=3,   # Minimum word length to consider
    keyword_top_n=10             # Number of top keywords to extract
)
```

### 3. Hybrid Approach (`hybrid`)

**How it works:**
- Combines TF-IDF and keyword matching with configurable weights
- Falls back to keyword-only if scikit-learn is not available
- Best for: Balanced approach capturing both semantic and exact matches

**Configuration:**
```python
config = SuggestionConfig(
    default_algorithm="hybrid",
    hybrid_tfidf_weight=0.6,     # Weight for TF-IDF score
    hybrid_keyword_weight=0.4    # Weight for keyword score
)
```

## Configuration

The engine is configured using the `SuggestionConfig` class:

```python
from app.ai_suggestions.config import SuggestionConfig

config = SuggestionConfig(
    min_confidence_threshold=0.3,   # Only create suggestions above this score (0.0-1.0)
    default_algorithm="tfidf",      # Algorithm to use: 'tfidf', 'keyword', or 'hybrid'
    tfidf_max_features=100,
    tfidf_ngram_range=(1, 2),
    keyword_min_word_length=3,
    keyword_top_n=10,
    hybrid_tfidf_weight=0.6,
    hybrid_keyword_weight=0.4
)
```

### Key Configuration Parameters

- **min_confidence_threshold** (0.0-1.0, default: 0.3): Only pairs with similarity scores above this threshold will generate suggestions. Lower values create more suggestions but with lower confidence.

- **default_algorithm** (default: "tfidf"): Which algorithm to use. Choose based on your needs:
  - `tfidf`: Best semantic understanding
  - `keyword`: Fastest, no dependencies
  - `hybrid`: Balanced approach

## API Usage

### Generate Suggestions

Trigger the suggestion engine to analyze all requirements and test cases:

```bash
# Use default configuration
curl -X POST "http://localhost:8000/api/v1/suggestions/generate"

# Override algorithm
curl -X POST "http://localhost:8000/api/v1/suggestions/generate?algorithm=keyword"

# Override threshold
curl -X POST "http://localhost:8000/api/v1/suggestions/generate?threshold=0.5"

# Override both
curl -X POST "http://localhost:8000/api/v1/suggestions/generate?algorithm=hybrid&threshold=0.4"
```

**Response:**
```json
{
  "message": "Suggestion generation completed",
  "results": {
    "pairs_analyzed": 100,
    "suggestions_created": 15,
    "suggestions_skipped": 85,
    "algorithm_used": "tfidf",
    "threshold": 0.3
  }
}
```

### Review Suggestions

After generation, suggestions can be reviewed through the existing endpoints:

```bash
# List all pending suggestions
curl "http://localhost:8000/api/v1/suggestions/pending"

# Get a specific suggestion
curl "http://localhost:8000/api/v1/suggestions/{suggestion_id}"

# Accept a suggestion
curl -X POST "http://localhost:8000/api/v1/suggestions/{suggestion_id}/review" \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted", "reviewed_by": "user@example.com"}'

# Reject a suggestion
curl -X POST "http://localhost:8000/api/v1/suggestions/{suggestion_id}/review" \
  -H "Content-Type: application/json" \
  -d '{"status": "rejected", "feedback": "Not relevant", "reviewed_by": "user@example.com"}'
```

## Engine Behavior

### Idempotency

The engine is idempotent - running it multiple times will not create duplicate suggestions:
- Skips pairs that already have a manual `RequirementTestCaseLink`
- Skips pairs that already have a pending `LinkSuggestion`
- Only creates new suggestions for previously unanalyzed pairs above threshold

### Text Analysis

The engine combines multiple fields from requirements and test cases:

**Requirements:**
- Title
- Description
- Module
- Tags

**Test Cases:**
- Title
- Description
- Preconditions
- Postconditions
- Steps
- Module
- Tags

## Adding New Algorithms

To add a new similarity algorithm:

1. **Create a new algorithm class** in `algorithms.py`:

```python
class MyCustomAlgorithm(SimilarityAlgorithm):
    def __init__(self, **kwargs):
        # Initialize your algorithm
        pass
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        # Implement your similarity computation
        # Must return a float between 0.0 and 1.0
        return similarity_score
```

2. **Update the factory function** in `algorithms.py`:

```python
def get_algorithm(algorithm_name: str, config=None) -> SimilarityAlgorithm:
    # ... existing code ...
    elif algorithm_name == "mycustom":
        return MyCustomAlgorithm(**kwargs)
```

3. **Update the configuration** in `config.py` if needed:

```python
class SuggestionConfig(BaseModel):
    # ... existing fields ...
    mycustom_param: int = Field(default=10)
```

4. **Update the method mapping** in `engine.py`:

```python
method_map = {
    'tfidf': SuggestionMethod.SEMANTIC_SIMILARITY,
    'keyword': SuggestionMethod.KEYWORD_MATCH,
    'hybrid': SuggestionMethod.HYBRID,
    'mycustom': SuggestionMethod.HEURISTIC  # or add new enum value
}
```

## Testing

Tests are located in `backend/tests/test_ai_suggestions.py`. Run tests with:

```bash
cd backend
pytest tests/test_ai_suggestions.py -v
```

## Performance Considerations

- **Computational complexity**: For N requirements and M test cases, the engine analyzes N×M pairs
- **Threshold tuning**: Higher thresholds reduce computation by creating fewer suggestions
- **Algorithm choice**: 
  - `keyword` is fastest
  - `tfidf` is slower but more accurate
  - `hybrid` is in between

For large datasets (>1000 requirements or test cases), consider:
- Running generation during off-peak hours
- Using the keyword algorithm for initial passes
- Increasing the threshold to reduce suggestions
- Implementing batch processing or incremental updates

## Troubleshooting

### "scikit-learn is required" error

If using `tfidf` algorithm and getting import errors:

```bash
pip install scikit-learn==1.3.2
```

Or switch to the `keyword` algorithm which has no dependencies:

```bash
curl -X POST "http://localhost:8000/api/v1/suggestions/generate?algorithm=keyword"
```

### Low number of suggestions generated

If you're getting fewer suggestions than expected:
- Lower the `threshold` parameter (default is 0.3)
- Check that requirements and test cases have sufficient text content
- Try the `hybrid` algorithm for broader matching

### Too many low-quality suggestions

If getting too many irrelevant suggestions:
- Increase the `threshold` parameter (try 0.5 or 0.6)
- Switch from `keyword` to `tfidf` for better semantic matching
- Review and tune algorithm-specific parameters
