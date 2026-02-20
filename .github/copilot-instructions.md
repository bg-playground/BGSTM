# Copilot Coding Agent Instructions

## Before Committing Any Python Changes

Always run the following commands from the `backend/` directory before committing:

```bash
cd backend
ruff check --fix .
ruff format .
mypy .
```

Fix any remaining errors reported by `mypy` before committing.

## Python Style Guidelines

- Use **Python 3.9+ native type annotations**:
  - `dict[str, Any]` not `Dict[str, Any]`
  - `list[str]` not `List[str]`
  - `str | None` not `Optional[str]`
  - `tuple[int, ...]` not `Tuple[int, ...]`
- Always end every file with a **trailing newline**.
- Keep imports **sorted** per ruff's `I001` isort rule (ruff will fix this automatically with `ruff check --fix .`).
- Do **not** import `Dict`, `List`, `Optional`, `Tuple` from `typing` unless targeting Python < 3.9.

## Frontend Changes

If you modify frontend files, run [Prettier](https://prettier.io/) to format them:

```bash
cd frontend
npx prettier --write .
```
