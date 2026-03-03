#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

# Optional: seed E2E test data after migrations
echo "Checking for E2E seed data..."
echo "  E2E_SEED_SQL='${E2E_SEED_SQL}'"
echo "  File exists: $([ -f "${E2E_SEED_SQL}" ] && echo 'yes' || echo 'no')"

if [ -n "${E2E_SEED_SQL}" ] && [ -f "${E2E_SEED_SQL}" ]; then
    echo "Seeding E2E test data from ${E2E_SEED_SQL}..."
    # Convert asyncpg URL to standard psql URL
    PSQL_URL=$(echo "${DATABASE_URL}" | sed 's|postgresql+asyncpg://|postgresql://|')
    psql "${PSQL_URL}" -f "${E2E_SEED_SQL}" || echo "WARNING: psql exited with a non-zero status (seed may already be applied or a constraint violation occurred)."
else
    echo "No E2E seed file found, skipping seed step."
fi

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
