# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.1.0] - 2026-09-09

BGSTM v2.1.0 is a methodology-maturity and reference-application capability release. It preserves the existing six-phase BGSTM methodology contract while substantially improving adoption guidance, traceability evidence, quality analysis, release-readiness workflows, and repository validation.

### Added
- Canonical end-to-end six-phase ShopFlow checkout worked example connecting requirements, risk, test design, environment readiness, execution evidence, analysis, and reporting (#405).
- Specialized ETL Semantic Validation example that applies all six BGSTM phases without introducing an additional methodology phase (#393).
- Quality KPI Dashboard capabilities for 7/30/90-day analysis, including execution/pass-rate trends, automation coverage, recurring-failure Pareto analysis, coverage-vs-failure-density analysis, and execution Mean Time to Recovery/time-to-green (#407, #408, #409).
- Shareable/saved Quality KPI filter state so dashboard windows and views can be restored through URL/local preferences (#372).
- Release-readiness KPI evidence in Markdown/PDF exports, using the selected dashboard window and bounded decision-relevant measures (#410).
- Scheduled Quality KPI digest foundation with per-user daily/weekly/off preferences, 7/30/90-day windows, deterministic one-shot dispatch, and initial in-app delivery (#411).
- Enhanced suggestion-review workflows with filtering, sorting, bulk review, keyboard shortcuts, and detailed preview support.
- Strict documentation quality validation: repository-wide Markdown link checking plus `mkdocs build --strict` in CI (#394, #399).
- Formal methodology maturity/release-readiness audit and phase-by-phase adoption assessment (#419).

### Changed
- Restored and made explicit the canonical BGSTM contract of **exactly six core testing phases**. ETL Semantic Validation is a specialized applied example, not Phase 7 (#393).
- Reworked the repository README, public documentation identity, Getting Started guidance, contributor instructions, and MkDocs metadata around **BGSTM — Better Global Software Testing Methodology** and a methodology-first adoption path (#395, #414).
- Clarified that Agile, Scrum, Waterfall, and hybrid approaches adapt BGSTM's cadence and governance without redefining its six phases.
- Established `docs/test-templates/` as the canonical template location while retaining `docs/templates/` only as a compatibility layer for historical links (#394).
- Finished and normalized practitioner guidance across the six canonical phase documents, including stronger execution-evidence guidance, canonical template links, and risk-based handoffs (#420).
- Tightened Phase 5 metric semantics: failed executions are not automatically unique defects; execution recovery/time-to-green is not defect MTTR; DRE/escape-rate measures require a trustworthy post-release defect source (#420).
- Repositioned the FastAPI/React software as an **optional reference application** that demonstrates selected BGSTM workflows rather than co-defining the methodology (#421).
- Improved repository discoverability and first-impression metadata, navigation, examples, and canonical-document structure.

### Fixed
- Hardened external case-result idempotency against expected uniqueness races while preserving unrelated database errors (#401).
- Migrated notification polling to AbortController-based cancellation and added post-await abort guards to multi-request frontend loaders (#402, #404).
- Corrected stale and broken documentation cross-links, removed the obsolete Phase 7 document, and reduced duplicate README/index content (#394).
- Corrected public documentation identity, license wording, and stale roadmap assumptions so the site matches the canonical repository baseline (#414).

### Release semantics and known limitations
- **Version choice:** v2.1.0 is a minor release because the public six-phase methodology contract remains compatible with v2.0.x while additive methodology guidance and reference-application capabilities have grown substantially. No intentional incompatible BGSTM phase or adoption contract is introduced.
- The Quality KPI reference application can derive execution recovery/time-to-green from execution history; it does **not** claim true defect MTTR without a defect lifecycle source.
- DRE and escape-rate metrics require trustworthy production/post-release defect data. Where that source is unavailable, those measures should remain unavailable rather than be inferred as zero.
- Scheduled KPI digests currently provide an **in-app delivery foundation**. Email/Slack adapters are deferred, and overlapping-dispatch idempotency is tracked as follow-up hardening (#423, #424).
- The Quality KPI feature page still needs a post-release documentation refresh to reflect the newest dashboard semantics and capabilities (#422); canonical Phase 5 guidance and this release record contain the authoritative metric distinctions for v2.1.0.
- The reference application remains optional. BGSTM can be adopted with other tools and platforms or without a custom application.

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
- **Notification System** — In-app notifications for suggestion generation, coverage drops, suggestion reviews, requirement/test case creation events; mark as read and mark all as read
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

[Unreleased]: https://github.com/bg-playground/BGSTM/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/bg-playground/BGSTM/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/bg-playground/BGSTM/releases/tag/v2.0.1
[2.0.0]: https://github.com/bg-playground/BGSTM/releases/tag/v2.0.0
[1.0.0]: https://github.com/bg-playground/BGSTM/releases/tag/v1.0.0
