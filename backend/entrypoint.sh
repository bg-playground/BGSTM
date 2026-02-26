#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

# Optional: seed E2E test data after migrations
if [ -n "${E2E_SEED_SQL}" ] && [ -f "${E2E_SEED_SQL}" ]; then
    echo "Seeding E2E test data from ${E2E_SEED_SQL}..."
    # Convert asyncpg URL to standard psql URL
    PSQL_URL=$(echo "${DATABASE_URL}" | sed 's|postgresql+asyncpg://|postgresql://|')
    psql "${PSQL_URL}" -f "${E2E_SEED_SQL}" || echo "Seed already applied (ignoring errors)."
fi

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
