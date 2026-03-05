# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.1] - 2026-03-05

### Fixed
- Fixed Docker backend failing to start on Windows clones due to CRLF line endings in `entrypoint.sh` (`exec /app/entrypoint.sh: no such file or directory`)
- Added `.gitattributes` to enforce LF line endings for shell scripts and all source files, preventing cross-platform line ending issues

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
