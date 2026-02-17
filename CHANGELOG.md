# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Traceability matrix API endpoint with coverage analysis and gap identification (#44)
- Metrics API endpoint with coverage percentage and suggestion acceptance rate (#44)
- CSV and JSON export for traceability matrix (#44)
- Frontend traceability matrix view and metrics dashboard (#44)
- React + TypeScript frontend with suggestion review dashboard, CRUD views, and manual link management (#43)
- Dockerfile and docker-compose.yml for containerized backend deployment (#42)
- GitHub Actions CI/CD pipeline for automated testing, linting, and type checking (#40)

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
- LICENSE file (Creative Commons Attribution 4.0 International)
- GitHub issue templates for bug reports, documentation improvements, feature requests, and template contributions
- Project labels: documentation, enhancement, templates, examples, integration
- Project milestones: v1.0 Core Framework, v1.1 Templates & Examples, v2.0 Traceability & AI Features, v3.0 App Integration

### Fixed
- Verified Phase 4 (Test Execution) and Phase 5 (Test Results Analysis) documentation completeness

### Changed
- Standardized all phase documentation to follow a uniform structure

[1.0.0]: https://github.com/bg-playground/BGSTM/releases/tag/v1.0.0
