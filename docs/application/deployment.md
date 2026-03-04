# Deployment Guide

## Quick Start with Docker Compose

The recommended way to run BGSTM is with Docker Compose, which starts PostgreSQL, the FastAPI backend, and the React frontend together.

```bash
# 1. Clone the repository
git clone https://github.com/bg-playground/BGSTM.git
cd BGSTM

# 2. Copy the example environment file and edit it
cp .env.example .env

# 3. Start all services
docker compose up -d

# 4. The application is now available at:
#    Frontend  → http://localhost:80
#    Backend   → http://localhost:8000
#    API docs  → http://localhost:8000/docs
```

Alternatively, use the platform-specific setup scripts:

```bash
# Linux / macOS
bash setup.sh

# Windows
setup.bat
```

## Environment Variables

All configuration is provided via environment variables (or an `.env` file). The backend reads these through `pydantic-settings`.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./bgstm.db` | SQLAlchemy async database URL. Use `postgresql+asyncpg://...` in production. |
| `SECRET_KEY` | `change-me-in-production-use-a-real-secret-key` | Secret used to sign JWT tokens. **Must be changed in production.** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT token lifetime in minutes |
| `ALGORITHM` | `HS256` | JWT signing algorithm |
| `API_V1_PREFIX` | `/api/v1` | URL prefix for all API routes |
| `PROJECT_NAME` | `BGSTM AI Traceability` | Application name shown in API docs |
| `VERSION` | `2.0.0` | Application version |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:3000","http://localhost:8000"]` | JSON array of allowed CORS origins |
| `AUTO_SUGGESTIONS_ENABLED` | `true` | Enable/disable AI suggestion generation |
| `AUTO_SUGGESTIONS_ALGORITHM` | `tfidf` | Suggestion algorithm: `tfidf`, `keyword`, or `hybrid` |
| `AUTO_SUGGESTIONS_THRESHOLD` | `0.3` | Minimum confidence score for surfacing suggestions (0.0–1.0) |
| `DEFAULT_ADMIN_EMAIL` | `admin@bgstm.local` | Email for the seeded admin account |
| `DEFAULT_ADMIN_PASSWORD` | `admin1234` | Password for the seeded admin account |
| `POSTGRES_USER` | `bgstm` | PostgreSQL username (Docker Compose) |
| `POSTGRES_PASSWORD` | `bgstm` | PostgreSQL password (Docker Compose) |
| `POSTGRES_DB` | `bgstm` | PostgreSQL database name (Docker Compose) |
| `POSTGRES_PORT` | `5432` | PostgreSQL host port (Docker Compose) |
| `BACKEND_PORT` | `8000` | Backend host port (Docker Compose) |
| `FRONTEND_PORT` | `80` | Frontend host port (Docker Compose) |

!!! danger "Production checklist"
    Before deploying to production:

    1. Set a strong, random `SECRET_KEY` (e.g. `openssl rand -hex 32`)
    2. Set a strong `DEFAULT_ADMIN_PASSWORD` (or disable seeding after first run)
    3. Set `DATABASE_URL` to a real PostgreSQL connection string
    4. Update `BACKEND_CORS_ORIGINS` to only include your actual frontend origin(s)

## Database Migrations (Alembic)

BGSTM uses Alembic for schema migrations.

```bash
# Inside the backend container (or a virtualenv with the backend deps installed)

# Apply all pending migrations
alembic upgrade head

# Create a new migration after changing a SQLAlchemy model
alembic revision --autogenerate -m "describe your change"

# Roll back one migration
alembic downgrade -1
```

When using Docker Compose, run migrations inside the backend container:

```bash
docker compose exec backend alembic upgrade head
```

## Development vs Production

| Concern | Development | Production |
|---|---|---|
| Database | SQLite (`sqlite+aiosqlite:///./bgstm.db`) | PostgreSQL (`postgresql+asyncpg://...`) |
| CORS origins | `localhost:3000`, `localhost:8000` | Your actual domain(s) only |
| Secret key | Any string | Strong random secret (`openssl rand -hex 32`) |
| Token expiry | 60 min (default) | Tune to your security policy |
| Container restart | Optional | `unless-stopped` (already set) |

## Health Check

```
GET /health
```

Returns `{"status": "healthy"}` when the backend is running. This endpoint requires no authentication and is used by the Docker Compose health check.

```bash
curl http://localhost:8000/health
```
