# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.1] - 2026-03-05

### Added
- Batch embedding for LLM similarity — `precompute_embeddings()` and `get_embeddings_batch()` methods to batch OpenAI API calls (up to 2048 texts per request) instead of N+M individual calls (#242)
- Persistent DB-backed embedding cache — new `embedding_cache` table, CRUD module, `load_cached_embeddings`/`save_embeddings_to_db` async methods, `compute_text_hash` utility (#243)
- Application documentation pages — new `docs/application/` section with authentication, API reference, notifications, audit logging, and deployment guides; fixed MkDocs license footer; removed dead `mike` config (#246)
- Automated GitHub Release workflow — tag-triggered `.github/workflows/release.yml` that extracts changelog sections and creates GitHub Releases; added "Releasing" section to CONTRIBUTING.md (#247)
- E2E test README and root README updates — added E2E badge, `🧪 Testing` section with all 7 spec files, environment variables, and Playwright instructions (#241)
- Enum binding regression tests — new `test_enum_binding.py` covering all enum columns (#231)

### Fixed
- Fixed PostgreSQL UUID type mismatch — `get_user` in `crud/user.py` now converts string IDs to `uuid.UUID`; `GUID.process_bind_param` coerces non-UUID values on PostgreSQL dialect (#226)
- Fixed SQLAlchemy enum case mismatch in core models — added `values_callable` to all `Enum()` column definitions in `requirement.py`, `test_case.py`, `suggestion.py`, `link.py` so lowercase values are sent to PostgreSQL (#230)
- Fixed SQLAlchemy enum case mismatch for `NotificationType` — applied same `values_callable` fix to `notification.py` (#231)
- Fixed remaining `notificationtype` enum mismatch and changed `version: int` to `version: int | None = None` in Pydantic schemas (#232)
- Fixed E2E test reliability: Playwright CI — Chromium-only in CI, fixed traceability test assertion, modal close race condition, increased download timeouts (#234)
- Fixed E2E test reliability: native dialog handling — delete confirmation now uses `page.once('dialog')` instead of DOM button lookup; fixed card title extraction; tightened traceability heading locator (#237)
- Fixed E2E test reliability: traceability matrix race condition — added `waitForResponse` for traceability API before `networkidle` (#240)
- Fixed mypy type errors — resolved `Result[Any].rowcount` attr-defined and `SimilarityAlgorithm` missing method errors with `isinstance` guard (#244)
- Fixed Docker backend failing to start on Windows clones due to CRLF line endings in `entrypoint.sh` (`exec /app/entrypoint.sh: no such file or directory`) (#248)
- Added `.gitattributes` to enforce LF line endings for shell scripts and all source files, preventing cross-platform line ending issues (#248)

### Changed
- Upgraded ESLint to v10 — bumped `eslint` to 10.0.2 and `@eslint/js` to 10.0.1 in frontend; added `.npmrc` with `legacy-peer-deps=true` (#233)

### Dependencies
- Bumped `fastapi` from 0.129.0 to 0.133.1 (#174)
- Bumped `email-validator` from 2.2.0 to 2.3.0 (#165)
- Bumped `@types/react-window` from 1.8.8 to 2.0.0 (#182)

## [2.0.0] - 2026-03-04

### Added
- **User Authentication & RBAC** — JWT-based authentication with admin, reviewer, and viewer roles; login, register, and logout flows
- **Notification System** — In-app notifications for suggestion generation, coverage drops, suggestion reviews, and requirement/test case creation events; mark as read and mark all as read
- **Audit Logging** — Full audit trail for all user actions including CRUD operations on requirements, test cases, links, and suggestions
- **Traceability Matrix View** — Visual matrix showing requirement-to-test-case coverage with filtering and PDF export
- **Metrics Dashboard** — Coverage metrics and suggestion statistics, exportable as CSV
- **E2E Test Suite** — Comprehensive Playwright end-to-end tests covering auth, CRUD, suggestions, RBAC, traceability, exports, and notifications; Docker Compose test environment (`docker-compose.test.yml`); CI workflow (`.github/workflows/e2e-tests.yml`)
- **AI Suggestion Engine Enhancements** — LLM embedding support (OpenAI & HuggingFace), batch embedding with caching, event-driven suggestion generation
- **Database Migrations** — Alembic migration system with versioned migrations for all tables (requirements, test_cases, link_suggestions, users, audit_log, notifications, performance indexes)
- **Docker & DevOps** — Full Docker Compose setup for production and testing, setup scripts (`setup.sh`, `setup.bat`), CI/CD workflows for backend, frontend, Docker, and E2E tests
- **MkDocs Documentation Site** — Material theme with dark/light mode, search, code copy, and GitHub Pages deployment; explicit nav with tabs covering all documentation sections

## [1.0.0] - 2026-02-17

### Added
- Core 6-phase documentation framework (Test Planning, Test Case Development, Test Environment Preparation, Test Execution, Test Results Analysis, Test Results Reporting)
- Methodology-specific considerations for Agile/Scrum and Waterfall across all phases
- Methodology guides: Agile, Scrum, Waterfall, and Methodology Comparison
- Documentation templates (7 total): test plan, test case, defect report, risk assessment, test execution report, test analysis report, metrics dashboard — all with field explanations
- Methodology-specific testing checklists for Agile, Scrum, and Waterfall
- Real-world ShopFlow e-commerce example artifacts for all 6 phases
- Phase 6 reporting examples: test summary report, sprint retrospective, release sign-off, metrics dashboard
- MkDocs Material documentation site with GitHub Pages deployment
- Professional branding: logo, favicon, blue theme
- FastAPI backend with SQLAlchemy data models (Requirement, TestCase, RequirementTestCaseLink, LinkSuggestion)
- Full CRUD API endpoints for requirements, test cases, and links
- AI suggestion engine with TF-IDF, keyword, and hybrid algorithms
- POST /api/v1/suggestions/generate endpoint
- Suggestion review API (accept/reject workflow)
- Comprehensive data model architecture documentation with ERD
- Multi-platform integration guide for building testing management applications
- Getting Started guide for new users
- CONTRIBUTING.md with contribution guidelines
- LICENSE file (MIT License)
- GitHub issue templates for bug reports, documentation improvements, feature requests, and template contributions
- Project labels: documentation, enhancement, templates, examples, integration
- Project milestones: v1.0 Core Framework, v1.1 Templates & Examples, v2.0 Traceability & AI Features, v3.0 App Integration

### Fixed
- Verified Phase 4 (Test Execution) and Phase 5 (Test Results Analysis) documentation completeness

### Changed
- Standardized all phase documentation to follow a uniform structure

[2.0.1]: https://github.com/bg-playground/BGSTM/releases/tag/v2.0.1
[2.0.0]: https://github.com/bg-playground/BGSTM/releases/tag/v2.0.0
[1.0.0]: https://github.com/bg-playground/BGSTM/releases/tag/v1.0.0
