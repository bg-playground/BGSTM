# Copilot Coding Agent Instructions for BGSTM

## Project invariants

These rules apply to every change unless a maintainer explicitly approves a project-level exception:

1. **BGSTM has exactly six core phases:**
   1. Test Planning
   2. Test Case Development
   3. Test Environment Preparation
   4. Test Execution
   5. Test Results Analysis
   6. Test Results Reporting
2. Specialized testing domains, including **ETL Semantic Validation**, are applications of those six phases and must not be introduced as additional methodology phases.
3. `docs/test-templates/` is the canonical template directory. `docs/templates/` exists only to preserve historical links; do not add new templates or new canonical links there.
4. Prefer one canonical document per subject. README/index files should navigate rather than duplicate large bodies of guidance.
5. BGSTM is primarily a **software testing methodology and knowledge base**. The FastAPI/React application in this repository is a reference implementation and must not silently redefine methodology concepts.

## Documentation changes

Before committing documentation work:

- preserve the six-phase terminology and numbering;
- place specialized applied examples under `docs/examples/` unless they are explicitly approved as core methodology;
- use canonical `docs/test-templates/` paths for templates;
- update `mkdocs.yml` when documentation navigation changes;
- run `python scripts/check_markdown_links.py` and fix all broken local targets;
- prefer concise cross-links over duplicated documentation that can drift.

## Python code standards

### Type annotations

- Use Python 3.9+ native type annotations:
  - `dict[str, Any]` not `Dict[str, Any]`
  - `list[str]` not `List[str]`
  - `tuple[int, str]` not `Tuple[int, str]`
  - `str | None` not `Optional[str]`
- Do not import `Dict`, `List`, `Tuple`, or `Optional` from `typing` for type hints.
- Non-generic `typing` imports such as `Any` and `TYPE_CHECKING` are acceptable.

### Code formatting (Ruff)

- Line length limit: **120 characters** (`backend/pyproject.toml`).
- Before committing Python changes, run:
  - `ruff check .`
  - `ruff format --check .`
- All files must end with a trailing newline.
- Keep imports grouped as standard library, third-party, then local application imports.

### Type checking (mypy)

- Target Python version: **3.11**.
- `ignore_missing_imports = true`.
- `disallow_untyped_defs = false`.
- `check_untyped_defs = false`.
- Disabled error codes include `var-annotated`, `assignment`, `arg-type`, and `misc`.
- Pydantic plugin is enabled; use `model_config = ConfigDict(from_attributes=True)` in Pydantic models where appropriate.
- Return type annotations must match actual return values.

### Testing

- Use `pytest` with `pytest-asyncio` for async tests.
- Use in-memory SQLite for database tests: `sqlite+aiosqlite:///:memory:`.
- Follow established patterns in `backend/tests/` rather than inventing parallel test infrastructure.
- Put backend test files in `backend/tests/`.

### Backend architecture

- Framework: **FastAPI** with async SQLAlchemy.
- Database models: `backend/app/models/`.
- CRUD operations: `backend/app/crud/`.
- API routes: `backend/app/api/`.
- Pydantic schemas: `backend/app/schemas/`.
- Services: `backend/app/services/`.
- Routers are registered in `backend/app/main.py`.
- Use `backend/app/db/session.py` for database session management.

## Frontend standards

- Framework: **React** with TypeScript.
- Use `useCallback` for event handlers passed as props or used in `useEffect` dependency arrays when it materially stabilizes references.
- Use `useMemo` for genuinely expensive computed values; do not memoize trivial expressions by default.
- Keep `useEffect` dependency arrays correct and complete.
- API clients live in `frontend/src/api/`.
- Page components live in `frontend/src/pages/`.

## Pull request standards

- Target `main` unless explicitly instructed otherwise.
- Do not create duplicate PRs for the same feature.
- Do not create separate "fix CI" PRs; fix the original PR.
- Keep PR scope focused and document validation performed.
- Do not make methodology-definition changes as incidental side effects of application or documentation work.

## CI expectations

Workflows are path-sensitive. Relevant checks may include:

- backend tests, Ruff lint/format, and mypy;
- frontend checks;
- Docker builds;
- Playwright end-to-end tests;
- security scanning;
- Documentation Links (`python scripts/check_markdown_links.py`).

Documentation-only changes may not trigger backend/frontend CI, but documentation link validation should pass before merge.
