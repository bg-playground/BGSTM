# BGSTM AI Traceability Backend

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+ (or SQLite for development)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your database settings
```

### Run Development Server

```bash
# Initialize database (tables will be created automatically on first run)
# Or load sample data which also initializes the database
python -m app.db.sample_data

# Start server
uvicorn app.main:app --reload
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application configuration
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── base.py          # Base model and mixins
│   │   ├── requirement.py   # Requirement model
│   │   ├── test_case.py     # TestCase model
│   │   ├── link.py          # RequirementTestCaseLink model
│   │   └── suggestion.py    # LinkSuggestion model
│   ├── schemas/             # Pydantic validation schemas
│   │   ├── requirement.py
│   │   ├── test_case.py
│   │   └── link.py
│   ├── api/                 # FastAPI route handlers
│   │   ├── requirements.py
│   │   ├── test_cases.py
│   │   └── links.py
│   ├── crud/                # Database CRUD operations
│   │   ├── requirement.py
│   │   ├── test_case.py
│   │   └── link.py
│   └── db/                  # Database session and utilities
│       ├── session.py       # Async session management
│       └── sample_data.py   # ShopFlow sample data loader
├── alembic/                 # Database migrations (future)
├── tests/                   # Unit and integration tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Database

### PostgreSQL (Production)
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/bgstm
```

### SQLite (Development)
```env
DATABASE_URL=sqlite+aiosqlite:///./bgstm.db
```

The application automatically creates tables on startup using SQLAlchemy's `create_all()`.

## Sample Data

Load the ShopFlow e-commerce sample data:

```bash
python -m app.db.sample_data
```

This creates:
- 5 Requirements (authentication, product search, cart, checkout, order tracking)
- 4 Test Cases (login, search, cart operations, checkout)
- 5 Manual Links between requirements and test cases

## API Endpoints

### Requirements
- `POST /api/v1/requirements` - Create a requirement
- `GET /api/v1/requirements` - List all requirements
- `GET /api/v1/requirements/{id}` - Get a specific requirement
- `PUT /api/v1/requirements/{id}` - Update a requirement
- `DELETE /api/v1/requirements/{id}` - Delete a requirement

### Test Cases
- `POST /api/v1/test-cases` - Create a test case
- `GET /api/v1/test-cases` - List all test cases
- `GET /api/v1/test-cases/{id}` - Get a specific test case
- `PUT /api/v1/test-cases/{id}` - Update a test case
- `DELETE /api/v1/test-cases/{id}` - Delete a test case

### Links
- `POST /api/v1/links` - Create a manual link
- `GET /api/v1/links` - List all links
- `GET /api/v1/links/{id}` - Get a specific link
- `GET /api/v1/requirements/{id}/links` - Get links for a requirement
- `GET /api/v1/test-cases/{id}/links` - Get links for a test case
- `DELETE /api/v1/links/{id}` - Delete a link

### Suggestions
- `GET /api/v1/suggestions` - List all suggestions
- `GET /api/v1/suggestions/pending` - List pending suggestions
- `GET /api/v1/suggestions/{id}` - Get a specific suggestion
- `POST /api/v1/suggestions/{id}/review` - Review a suggestion (accept/reject)

## Development

### Running with Auto-reload
```bash
uvicorn app.main:app --reload --port 8000
```

### Environment Variables
Create a `.env` file from `.env.example` and customize:

```env
DATABASE_URL=sqlite+aiosqlite:///./bgstm.db
API_V1_PREFIX=/api/v1
PROJECT_NAME=BGSTM AI Traceability
VERSION=2.0.0
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

## Testing

```bash
pytest
```

## Architecture

See [Data Model Architecture](../docs/architecture/data-model-diagram.md) for:
- Entity-Relationship Diagram
- Database schema details
- Design principles
- AI integration points

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy 2.0**: SQL toolkit and ORM with async support
- **Pydantic**: Data validation using Python type hints
- **PostgreSQL**: Primary production database
- **SQLite**: Development and testing database
- **Uvicorn**: ASGI server

## Contributing

1. Follow the existing code structure
2. Add type hints to all functions
3. Update tests for new features
4. Run linters before committing

## License

See [LICENSE](../LICENSE) file for details.
