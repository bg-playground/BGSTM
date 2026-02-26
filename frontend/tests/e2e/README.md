# BGSTM End-to-End Tests

This directory contains the Playwright end-to-end test suite for the BGSTM application.

## Prerequisites

- [Node.js](https://nodejs.org/) v20+
- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) (for the full stack test environment)
- A running BGSTM frontend and backend (locally or via Docker)

---

## Installation

Install Playwright and its browser binaries from the `frontend/` directory:

```bash
cd frontend
npm install
npx playwright install
```

To install only the Chromium browser (faster, used in CI):

```bash
npx playwright install --with-deps chromium
```

---

## Running Tests Locally

### Against a locally running dev server

1. Start the backend and frontend dev server:

   ```bash
   # In one terminal – start the backend
   cd backend
   uvicorn app.main:app --reload --port 8000

   # In another terminal – start the frontend Vite dev server
   cd frontend
   npm run dev  # runs on http://localhost:3000
   ```

2. Seed the database with test data (optional but recommended):

   ```bash
   psql -U bgstm -d bgstm < frontend/tests/e2e/fixtures/seed.sql
   ```

3. Run the tests:

   ```bash
   cd frontend
   npm run test:e2e
   ```

### Headed mode (visible browser)

```bash
cd frontend
npm run test:e2e:headed
```

### Interactive UI mode

```bash
cd frontend
npm run test:e2e:ui
```

---

## Running Tests with Docker Compose

The `docker-compose.test.yml` file at the project root spins up a self-contained test environment including a seeded PostgreSQL database, the FastAPI backend, and the production Nginx frontend build.

```bash
# From the project root
docker compose -f docker-compose.test.yml up -d

# Wait for services to be healthy, then run tests
cd frontend
PLAYWRIGHT_BASE_URL=http://localhost:3001 \
PLAYWRIGHT_API_URL=http://localhost:8001 \
npx playwright test

# Tear down when done
cd ..
docker compose -f docker-compose.test.yml down -v
```

---

## Viewing the HTML Report

After a test run, Playwright generates an HTML report in `frontend/playwright-report/`.

```bash
cd frontend
npx playwright show-report
```

This opens an interactive report in your browser showing passed/failed tests, traces, and screenshots.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PLAYWRIGHT_BASE_URL` | `http://localhost:3000` | Frontend base URL |
| `PLAYWRIGHT_API_URL` | `http://localhost:8000` | Backend API base URL |
| `E2E_ADMIN_EMAIL` | `admin@test.com` | Admin user email for tests |
| `E2E_ADMIN_PASSWORD` | `password123` | Admin user password for tests |

---

## Test Structure

```
frontend/tests/e2e/
├── auth.spec.ts          # Login, register, logout, protected route access
├── suggestions.spec.ts   # Suggestion dashboard: filters, accept, reject
├── crud.spec.ts          # Requirements and test case CRUD operations
├── exports.spec.ts       # CSV and PDF export downloads
├── notifications.spec.ts # Notification bell lifecycle
├── helpers/
│   ├── auth.ts           # Reusable login() / logout() helpers
│   └── api.ts            # Direct API call helpers for setup/cleanup
└── fixtures/
    └── seed.sql          # SQL seed for the test database
```

---

## Adding New Tests

1. Create a new `*.spec.ts` file in `frontend/tests/e2e/`.
2. Import helpers as needed:

   ```typescript
   import { test, expect } from '@playwright/test';
   import { login } from './helpers/auth';
   import { apiLogin, apiCreateRequirement } from './helpers/api';
   ```

3. Use `test.beforeEach` to authenticate and navigate to the correct page.
4. Use `test.skip()` to conditionally skip tests when the required UI element is not present in the current seed data.
5. Run `npm run test:e2e` to verify your new tests pass.

---

## CI Integration

The `.github/workflows/e2e-tests.yml` workflow runs on every pull request and push to `main` that touches frontend or backend code. It:

1. Starts the full stack via `docker-compose.test.yml`.
2. Waits for health checks to pass.
3. Runs Playwright against Chromium only (to keep CI fast).
4. Uploads the HTML report and screenshots as artifacts on failure.
