# BGSTM Reference Application

BGSTM is the **Better Global Software Testing Methodology**: a methodology-agnostic framework organized around exactly six core testing phases. The methodology does not require this repository's software stack, application, or automation features in order to be adopted.

This repository also includes an **optional reference application** that demonstrates how selected BGSTM practices can be supported in software. It provides working examples of requirements traceability, AI-assisted test-case suggestions, coverage and quality dashboards, reporting, notifications, auditability, and related testing-management workflows.

The reference application is an implementation example, not the definition of BGSTM. Teams can apply the six-phase methodology with different tools, platforms, delivery models, or no custom application at all.

## Architecture Overview

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), Alembic |
| Frontend | React, TypeScript |
| Database | PostgreSQL (production), SQLite (development/tests) |
| Auth | JWT (HS256), bcrypt password hashing |
| Containerisation | Docker, Docker Compose |

The reference application's backend exposes a RESTful JSON API at `/api/v1` and serves interactive documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).

## Application Pages

- [Authentication & RBAC](authentication.md) — User registration, login, JWT tokens, and role-based access control
- [API Reference](api-reference.md) — Endpoint reference for the reference application
- [Notifications](notifications.md) — Event-driven notification system
- [Audit Logging](audit-logging.md) — Immutable audit trail for write operations
- [Deployment Guide](deployment.md) — Docker Compose setup, environment variables, and production configuration
