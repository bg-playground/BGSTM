#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

# Optional: seed test data after migrations.
# Set SEED_SQL_PATH to an absolute path to a SQL file to run it after migrations.
# This is used by the E2E test Docker Compose environment.
if [ -n "$SEED_SQL_PATH" ] && [ -f "$SEED_SQL_PATH" ]; then
    echo "Running seed SQL from $SEED_SQL_PATH ..."
    # Use psql (postgresql-client is installed in the Dockerfile)
    # Extract host/port/user/db from DATABASE_URL
    # DATABASE_URL format: postgresql+asyncpg://user:pass@host:port/db
    # Strip the +asyncpg driver prefix for psql
    PSQL_URL=$(echo "$DATABASE_URL" | sed 's|postgresql+asyncpg://|postgresql://|')
    psql "$PSQL_URL" -f "$SEED_SQL_PATH"
    echo "Seed SQL complete."
fi

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
