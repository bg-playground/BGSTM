# BGSTM AI Traceability Backend

## Quick Start

### Prerequisites
- **Docker & Docker Compose** (recommended) OR
- Python 3.11+ and PostgreSQL 14+ (for local development)

### Option 1: Run with Docker (Recommended)

```bash
# From project root directory
# Copy environment file and customize if needed
cp .env.example .env

# Start all services (backend + PostgreSQL)
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Stop services and remove volumes
docker-compose down -v
```

The backend API will be available at http://localhost:8000

### Option 2: Run Locally with Docker Build

```bash
# Build the Docker image
cd backend
docker build -t bgstm-backend .

# Run the container (requires PostgreSQL running separately)
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:password@host/bgstm" \
  -e PYTHONPATH=/app \
  --name bgstm-backend \
  bgstm-backend

# View logs
docker logs -f bgstm-backend

# Stop and remove container
docker stop bgstm-backend && docker rm bgstm-backend
```

### Option 3: Local Development (Without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your database settings

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
# For PostgreSQL (Docker): DATABASE_URL=postgresql+asyncpg://bgstm:bgstm@db:5432/bgstm
API_V1_PREFIX=/api/v1
PROJECT_NAME=BGSTM AI Traceability
VERSION=2.0.0
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
PYTHONPATH=/app
```

## Testing

### Run Tests Locally
```bash
pytest
```

### Run Tests Inside Docker Container
```bash
# Using docker-compose
docker-compose exec backend pytest

# Or build and run tests in a separate container
docker build -f backend/Dockerfile -t bgstm-backend-test backend/
docker run --rm bgstm-backend-test pytest
```

## Docker Configuration

### Environment Variables for Docker

When using Docker or docker-compose, configure these variables in your `.env` file:

```env
# Database (PostgreSQL for Docker)
DATABASE_URL=postgresql+asyncpg://bgstm:bgstm@db:5432/bgstm
POSTGRES_USER=bgstm
POSTGRES_PASSWORD=bgstm
POSTGRES_DB=bgstm
POSTGRES_PORT=5432

# Backend
BACKEND_PORT=8000
API_V1_PREFIX=/api/v1
PROJECT_NAME=BGSTM AI Traceability
VERSION=2.0.0
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
PYTHONPATH=/app
```

### Docker Commands Reference

```bash
# Build backend image
docker build -t bgstm-backend backend/

# Run backend container (standalone)
docker run -p 8000:8000 -e DATABASE_URL="..." bgstm-backend

# Using docker-compose
docker-compose up -d          # Start in background
docker-compose up             # Start with logs
docker-compose down           # Stop all services
docker-compose logs -f        # View logs
docker-compose ps             # List running services
docker-compose exec backend bash  # Access backend shell
```

### Loading Sample Data with Docker

```bash
# Load ShopFlow sample data
docker-compose exec backend python -m app.db.sample_data
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
