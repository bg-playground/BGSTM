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

### 4. LLM Embeddings (`llm`) **NEW**

**How it works:**
- Uses large language model embeddings (OpenAI or HuggingFace) to capture deep semantic meaning
- Computes cosine similarity between embedding vectors
- Supports caching for improved performance
- Best for: Highest accuracy semantic understanding, capturing context, synonyms, and conceptual relationships

**Requirements:**
- For OpenAI: `openai>=1.0.0` and `OPENAI_API_KEY` environment variable
- For HuggingFace: `sentence-transformers>=2.2.0`

**Pros:**
- Superior semantic understanding compared to TF-IDF
- Captures context, synonyms, and conceptual relationships
- Understands complex language patterns
- Works well with domain-specific terminology

**Cons:**
- OpenAI requires API key and has usage costs
- HuggingFace models download on first use (slower initially)
- Higher latency compared to keyword matching
- Requires additional dependencies

**Configuration:**
```python
# Using OpenAI (default)
config = SuggestionConfig(
    default_algorithm="llm",
    llm_provider="openai",
    llm_model="text-embedding-3-small",  # or "text-embedding-3-large"
    llm_cache_embeddings=True
)

# Using HuggingFace (runs locally)
config = SuggestionConfig(
    default_algorithm="llm",
    llm_provider="huggingface",
    llm_model="sentence-transformers/all-MiniLM-L6-v2",
    llm_cache_embeddings=True
)
```

**Setup Instructions:**

For **OpenAI**:
1. Install the package: `pip install openai>=1.0.0`
2. Set your API key: `export OPENAI_API_KEY="your-api-key"`
3. Or add to `.env` file: `OPENAI_API_KEY=your-api-key`

For **HuggingFace**:
1. Install the package: `pip install sentence-transformers>=2.2.0`
2. Models download automatically on first use
3. No API key required (runs locally)

**Performance Considerations:**
- **Caching**: Embeddings are cached in memory by default to avoid redundant API calls/computations
- **OpenAI Costs**: OpenAI charges per embedding (~$0.0001 per 1K tokens for text-embedding-3-small)
- **HuggingFace**: First run downloads model (~90MB for all-MiniLM-L6-v2), subsequent runs are faster
- **Batch Processing**: For large datasets, consider processing in batches during off-peak hours

**When to Use:**
- Use LLM for highest accuracy when API access is available
- Use HuggingFace provider for local deployment without API dependencies
- Keep TF-IDF as default for most users (no API key required, good balance of speed and accuracy)

## Configuration

The engine is configured using the `SuggestionConfig` class:

```python
from app.ai_suggestions.config import SuggestionConfig

config = SuggestionConfig(
    min_confidence_threshold=0.3,   # Only create suggestions above this score (0.0-1.0)
    default_algorithm="tfidf",      # Algorithm to use: 'tfidf', 'keyword', 'hybrid', or 'llm'
    tfidf_max_features=100,
    tfidf_ngram_range=(1, 2),
    keyword_min_word_length=3,
    keyword_top_n=10,
    hybrid_tfidf_weight=0.6,
    hybrid_keyword_weight=0.4,
    # LLM settings (only needed if using 'llm' algorithm)
    llm_provider="openai",          # 'openai' or 'huggingface'
    llm_model=None,                 # Optional: model override
    llm_cache_embeddings=True       # Cache embeddings for performance
)
```

### Key Configuration Parameters

- **min_confidence_threshold** (0.0-1.0, default: 0.3): Only pairs with similarity scores above this threshold will generate suggestions. Lower values create more suggestions but with lower confidence.

- **default_algorithm** (default: "tfidf"): Which algorithm to use. Choose based on your needs:
  - `tfidf`: Best semantic understanding (traditional ML)
  - `keyword`: Fastest, no dependencies
  - `hybrid`: Balanced approach
  - `llm`: Highest accuracy with LLM embeddings (requires API key or model download)

## API Usage

### Generate Suggestions

Trigger the suggestion engine to analyze all requirements and test cases:

```bash
# Use default configuration
curl -X POST "http://localhost:8000/api/v1/suggestions/generate"

# Override algorithm
curl -X POST "http://localhost:8000/api/v1/suggestions/generate?algorithm=keyword"

# Use LLM algorithm (requires OpenAI API key or HuggingFace model)
curl -X POST "http://localhost:8000/api/v1/suggestions/generate?algorithm=llm"

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
    'llm': SuggestionMethod.LLM_EMBEDDING,
    'mycustom': SuggestionMethod.HEURISTIC  # or add new enum value
}
```

5. **Update the API endpoint** in `api/suggestions.py` to accept the new algorithm name.

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
  - `llm` has the highest accuracy but also highest latency and potential costs

For large datasets (>1000 requirements or test cases), consider:
- Running generation during off-peak hours
- Using the keyword algorithm for initial passes
- Increasing the threshold to reduce suggestions
- Implementing batch processing or incremental updates
- For LLM: Enable caching and consider HuggingFace for cost-free local processing

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

### "OpenAI library not installed" or "OPENAI_API_KEY not set" errors

If using `llm` algorithm with OpenAI provider:

```bash
# Install OpenAI library
pip install openai>=1.0.0

# Set API key in environment
export OPENAI_API_KEY="your-api-key-here"

# Or add to .env file
echo "OPENAI_API_KEY=your-api-key-here" >> .env
```

Or use HuggingFace provider (no API key needed):

```bash
# Install sentence-transformers
pip install sentence-transformers>=2.2.0

# In your config, set provider to huggingface
# Or use environment variable in .env:
echo "LLM_PROVIDER=huggingface" >> .env
```

### Low number of suggestions generated

If you're getting fewer suggestions than expected:
- Lower the `threshold` parameter (default is 0.3)
- Check that requirements and test cases have sufficient text content
- Try the `hybrid` or `llm` algorithm for broader matching

### Too many low-quality suggestions

If getting too many irrelevant suggestions:
- Increase the `threshold` parameter (try 0.5 or 0.6)
- Switch from `keyword` to `tfidf` or `llm` for better semantic matching
- Review and tune algorithm-specific parameters
