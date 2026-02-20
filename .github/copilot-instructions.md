# Copilot Coding Agent Instructions for BGSTM

## Python Code Standards

### Type Annotations
- **ALWAYS** use Python 3.9+ native type annotations:
  - `dict[str, Any]` NOT `Dict[str, Any]`
  - `list[str]` NOT `List[str]`
  - `tuple[int, str]` NOT `Tuple[int, str]`
  - `str | None` NOT `Optional[str]`
- Do NOT import `Dict`, `List`, `Tuple`, `Optional` from `typing` for type hints — use native Python types instead
- The only valid `typing` imports are: `Any`, `TYPE_CHECKING`, and similar non-generic types

### Code Formatting (Ruff)
- Line length limit is **120 characters** (configured in `backend/pyproject.toml`)
- Before committing, ensure all Python files pass:
  - `ruff check .` (linting — rules: E, F, W, I)
  - `ruff format .` (formatting)
- **All files MUST end with a trailing newline** (W292)
- **Imports MUST be sorted** according to isort rules (I001):
  - Standard library imports first
  - Third-party imports second
  - Local application imports third
  - Each group separated by a blank line

### Type Checking (mypy)
- Target Python version: **3.11**
- `ignore_missing_imports = true` — don't worry about third-party type stubs
- `disallow_untyped_defs = false` — untyped function defs are allowed
- `check_untyped_defs = false` — untyped function bodies are not checked
- Disabled error codes: `var-annotated`, `assignment`, `arg-type`, `misc`
- Pydantic plugin is enabled — use `model_config = ConfigDict(from_attributes=True)` in Pydantic models
- Ensure return type annotations match actual return types (e.g., don't annotate `-> dict[str, list[dict[str, Any]]]` when the function returns `dict[str, Any]`)

### Testing
- Use `pytest` with `pytest-asyncio` for async tests
- Use in-memory SQLite for database tests: `sqlite+aiosqlite:///:memory:`
- Follow the pattern in `backend/tests/test_traceability.py`:
  ```python
  engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
  async with engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)
  AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
  ```
- All test files go in `backend/tests/`

### Backend Architecture
- Framework: **FastAPI** with async SQLAlchemy
- Database models in `backend/app/models/`
- CRUD operations in `backend/app/crud/`
- API routes in `backend/app/api/`
- Schemas (Pydantic) in `backend/app/schemas/`
- Services in `backend/app/services/`
- All routers registered in `backend/app/main.py`
- Use `backend/app/db/session.py` for database session management

### Frontend Standards
- Framework: **React** with TypeScript
- Use `useCallback` for all event handler functions passed as props or used in `useEffect` dependency arrays
- Use `useMemo` for expensive computed values
- All `useEffect` hooks must have correct dependency arrays
- API client files in `frontend/src/api/`
- Page components in `frontend/src/pages/`

## PR Standards
- Target branch for all PRs: **`main`** (unless explicitly told otherwise)
- Do NOT create duplicate PRs for the same feature
- Do NOT create separate "fix CI" PRs — fix issues in the original PR instead
- Each PR should pass all three CI jobs: **Test**, **Lint**, **Type Check**

## CI Pipeline
The CI runs three jobs on every PR:
1. **Test** — `pytest` in `backend/`
2. **Lint** — `ruff check .` and `ruff format --check .` in `backend/` (auto-fix step runs first on PRs)
3. **Type Check** — `mypy .` in `backend/`

There is also an auto-fix step that runs `ruff check --fix` and `ruff format` and commits the result, but code should be clean BEFORE pushing to avoid unnecessary fix commits.
