# Contributing to BGSTM

Thank you for contributing to **BGSTM (Better Global Software Testing Methodology)**. Contributions are welcome across methodology documentation, templates, worked examples, integrations, and the reference application.

## Methodology invariants

Before changing documentation or application behavior that represents BGSTM concepts, preserve these project-level rules:

1. **BGSTM has exactly six core phases:** Test Planning, Test Case Development, Test Environment Preparation, Test Execution, Test Results Analysis, and Test Results Reporting.
2. Specialized domains such as ETL semantic validation **apply the six phases**; they do not create additional phases.
3. `docs/test-templates/` is the **canonical template directory**. `docs/templates/` exists only as a compatibility layer for historical links and should not receive new templates or new documentation links.
4. Prefer **one canonical document per subject**. README/index pages should primarily navigate to substantive documents instead of duplicating them.

## Ways to contribute

You can help by:

- improving methodology guidance, clarity, and consistency;
- contributing or refining practical templates and examples;
- reporting defects, inconsistencies, or broken documentation;
- improving the FastAPI/React reference application;
- extending automation, traceability, dashboards, or integration support;
- improving tests, CI, security, accessibility, and developer experience.

## Getting started

### Prerequisites

For documentation-only work, a GitHub account and basic Git/Markdown familiarity are sufficient. Application development may also require Python 3.11+, Node.js/npm, Docker, and Docker Compose depending on the area being changed.

### Set up your branch

```bash
git clone https://github.com/YOUR-USERNAME/BGSTM.git
cd BGSTM
git checkout -b feature/your-feature-name
```

For backend work:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Repository structure

```text
docs/
├── phases/             # Canonical six-phase methodology guidance
├── methodologies/      # Agile, Scrum, Waterfall, comparison guidance
├── test-templates/     # Canonical testing templates
├── templates/          # Legacy-link compatibility only; do not add new content here
├── examples/           # Practical and specialized BGSTM examples
├── integration/        # Integration and application guidance
├── features/           # Feature documentation
└── specs/              # API/contracts and specifications

backend/                # FastAPI backend
frontend/               # React/TypeScript frontend
scripts/                # Repository validation/support scripts
.github/workflows/      # CI and automation
```

## Making changes

### Documentation

- Put new templates in `docs/test-templates/`.
- Put worked or domain-specific applications in `docs/examples/` unless they are truly part of the core methodology.
- Do not introduce new BGSTM phases without an explicit project-level methodology decision.
- Prefer links to canonical material over repeating large blocks of content in multiple README/index files.
- Keep relative links valid and run the repository link checker before submitting documentation changes.

```bash
python scripts/check_markdown_links.py
```

If MkDocs navigation is affected, also review `mkdocs.yml` for consistency.

### Backend

```bash
cd backend
pytest
ruff check .
ruff format --check .
mypy .
```

### Frontend

```bash
cd frontend
npm install
npm run lint
npm run type-check
```

For end-to-end changes, see [`frontend/tests/e2e/README.md`](frontend/tests/e2e/README.md).

## Pull request process

Before submitting a pull request:

1. Search existing issues and pull requests to avoid duplicate work.
2. Keep the change focused and explain the problem it solves.
3. Run the checks relevant to the files you changed.
4. Update documentation when behavior, contracts, or navigation changes.
5. Confirm methodology terminology remains consistent with the six-phase model.

Use descriptive commit messages such as:

- `docs: clarify test planning guidance`
- `fix: correct traceability export behavior`
- `feat: add release readiness filter`
- `test: cover notification lifecycle`

A pull request should include a concise summary, relevant issue references, and the validation performed. Address CI failures in the original PR rather than opening a separate fix PR.

## CI checks

Different workflows run depending on the paths changed. The repository includes checks for:

- backend tests, linting, formatting, and type checking;
- frontend linting/type checks and end-to-end Playwright coverage;
- Docker builds;
- security scanning;
- internal Markdown link integrity;
- strict MkDocs builds for documentation changes.

A documentation-only pull request may not run backend/frontend jobs, but Documentation Quality should validate Markdown targets and the strict MkDocs build.

## Releasing

BGSTM uses the root [`CHANGELOG.md`](CHANGELOG.md) as the canonical release record and follows Semantic Versioning.

Before creating a release:

1. Reconcile material changes since the previous release and move them from `Unreleased` into the new version section.
2. Choose the version from compatibility and semantic scope rather than issue count or elapsed time.
3. Ensure required CI and documentation checks are green on the release candidate commit.
4. Merge the release-baseline pull request to `main`.
5. Create and push an annotated `vX.Y.Z` tag at the verified `main` commit.
6. Confirm the tag-triggered **Release** workflow succeeds and creates the GitHub Release.
7. Verify the published release body matches the corresponding root changelog section.

The release workflow extracts notes from the root `CHANGELOG.md`; `docs/CHANGELOG.md` is only a documentation-site pointer to that canonical file.

## Documentation style

Use clear, professional language and existing naming conventions. Prefer:

- concise paragraphs and descriptive headings;
- American English spelling;
- active voice where practical;
- concrete examples where they improve understanding;
- lowercase, hyphenated filenames such as `test-planning.md`;
- canonical cross-links rather than duplicated guidance.

## Reporting issues

Use the repository issue templates when possible. Include enough context to reproduce or evaluate the problem, including the affected file/feature, expected behavior, actual behavior, and relevant evidence.

Common labels include `bug`, `enhancement`, `documentation`, `good first issue`, `help wanted`, and `question`.

## Additional resources

- [Repository README](README.md)
- [Getting Started Guide](docs/GETTING-STARTED.md)
- [Complete Documentation](docs/README.md)
- [Six BGSTM Phases](docs/phases/index.md)
- [Canonical Test Templates](docs/test-templates/README.md)
- [Worked Examples](docs/examples/README.md)
- [MIT License](LICENSE)

Thank you for helping keep BGSTM useful, consistent, and practical for the software testing community.
