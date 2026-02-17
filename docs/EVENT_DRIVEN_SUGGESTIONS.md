# Event-Driven AI Suggestion Generation

## Overview
The BGSTM system now automatically generates AI-powered link suggestions when requirements or test cases are created or updated. This eliminates the need to manually trigger suggestion generation and ensures new items are immediately analyzed for potential links.

## How It Works

### Automatic Trigger Points
Suggestions are automatically generated in the background when:
- A new requirement is created → Generates suggestions against all existing test cases
- A requirement is updated → Generates suggestions against all existing test cases
- A new test case is created → Generates suggestions against all existing requirements
- A test case is updated → Generates suggestions against all existing requirements

### Non-Blocking Operation
- All suggestion generation runs as a background task using FastAPI's BackgroundTasks
- API responses return immediately without waiting for suggestion generation to complete
- No impact on API response times

### Intelligent Processing
- Only creates suggestions when similarity scores exceed the configured threshold
- Automatically avoids duplicate suggestions
- Skips pairs that already have confirmed links
- Uses the same algorithms and logic as manual generation

## Configuration

Configure the feature via environment variables in `.env` or system environment:

```bash
# Enable/disable auto-suggestions
AUTO_SUGGESTIONS_ENABLED=true

# Algorithm to use: 'tfidf', 'keyword', or 'hybrid'
AUTO_SUGGESTIONS_ALGORITHM=tfidf

# Minimum similarity threshold (0.0 to 1.0)
AUTO_SUGGESTIONS_THRESHOLD=0.3
```

### Algorithm Options
- **tfidf**: TF-IDF with cosine similarity (default) - best for semantic matching
- **keyword**: Keyword extraction and matching - fast, good for exact matches
- **hybrid**: Weighted combination of TF-IDF + keyword - balanced approach

### Threshold
- Range: 0.0 to 1.0
- Default: 0.3
- Lower values create more suggestions (higher recall, lower precision)
- Higher values create fewer, more confident suggestions (lower recall, higher precision)

## Usage Examples

### Creating a Requirement
```python
import requests

# Create requirement - suggestions generated automatically in background
response = requests.post(
    "http://localhost:8000/api/v1/requirements",
    json={
        "title": "User Authentication",
        "description": "System shall authenticate users with credentials",
        "type": "functional",
        "priority": "high",
        "status": "approved"
    }
)

# Response returns immediately
print(response.json())  # Returns requirement details

# Suggestions available shortly after (background task completes)
suggestions = requests.get("http://localhost:8000/api/v1/suggestions")
```

### Creating a Test Case
```python
# Create test case - suggestions generated automatically in background
response = requests.post(
    "http://localhost:8000/api/v1/test-cases",
    json={
        "title": "Test user authentication",
        "description": "Verify users can authenticate with valid credentials",
        "type": "functional",
        "priority": "high",
        "status": "ready",
        "automation_status": "automated"
    }
)
```

### Disabling Auto-Suggestions
If you want to disable auto-suggestions and only use manual generation:

```bash
# In .env file
AUTO_SUGGESTIONS_ENABLED=false
```

## Manual Generation Still Available

You can still trigger manual suggestion generation for the entire corpus:

```bash
# Generate suggestions for all pairs with default settings
curl -X POST http://localhost:8000/api/v1/suggestions/generate

# With custom algorithm and threshold
curl -X POST "http://localhost:8000/api/v1/suggestions/generate?algorithm=keyword&threshold=0.2"
```

## Monitoring

The event-driven system includes logging for monitoring:

```python
# Logs include:
# - "Starting auto-suggestion generation for requirement {id}"
# - "Auto-suggestion completed: X created, Y skipped"
# - Error logs if generation fails
```

Check your application logs to monitor background task execution.

## Performance Considerations

### Scalability
- Background tasks are lightweight and non-blocking
- Each task only analyzes the new/modified item against existing items (not full corpus)
- Database queries are optimized with proper indexing

### Best Practices
1. **For Large Datasets**: Keep threshold at 0.3 or higher to limit suggestion volume
2. **For New Projects**: Can lower threshold to 0.2 to discover more potential links
3. **For High Velocity**: Consider increasing threshold to reduce background processing

### Resource Usage
- Memory: Minimal - only loads items for comparison
- CPU: Varies by algorithm (keyword < tfidf < hybrid)
- Database: Efficient queries with proper indexes

## Troubleshooting

### No Suggestions Created
If auto-suggestions aren't being created:

1. **Check Configuration**:
   ```python
   from app.config import settings
   print(settings.AUTO_SUGGESTIONS_ENABLED)  # Should be True
   ```

2. **Check Similarity Scores**: The items may not exceed the threshold
   ```bash
   # Try manual generation with lower threshold to test
   curl -X POST "http://localhost:8000/api/v1/suggestions/generate?threshold=0.1"
   ```

3. **Check Logs**: Look for error messages in application logs

### Performance Issues
If background tasks are causing performance issues:

1. Increase the threshold to reduce suggestion volume
2. Switch to 'keyword' algorithm for faster processing
3. Consider disabling auto-suggestions during bulk imports

## Migration from Manual Generation

Existing workflows continue to work:
- Manual `/api/v1/suggestions/generate` endpoint still available
- Existing suggestions are preserved
- No changes to suggestion review workflow
- All existing API contracts maintained

## Testing

Run tests to verify the feature:

```bash
cd backend
pytest tests/test_event_driven_suggestions.py -v
```

All tests should pass:
- ✅ Auto-suggestion on requirement creation
- ✅ Auto-suggestion on test case creation  
- ✅ No duplicate suggestions
- ✅ Threshold enforcement
- ✅ Multiple item scenarios
- ✅ Algorithm configuration
