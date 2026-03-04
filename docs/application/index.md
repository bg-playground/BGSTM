# BGSTM Application

BGSTM is both a **testing methodology framework** and a **full-stack web application** that puts that methodology into practice. The application automates requirements traceability, AI-powered test case suggestions, coverage analysis, and audit logging — all behind a secure role-based API.

## Architecture Overview

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy (async), Alembic |
| Frontend | React, TypeScript |
| Database | PostgreSQL (production), SQLite (development/tests) |
| Auth | JWT (HS256), bcrypt password hashing |
| Containerisation | Docker, Docker Compose |

The backend exposes a RESTful JSON API at `/api/v1` and serves interactive documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc).

## Application Pages

- [Authentication & RBAC](authentication.md) — User registration, login, JWT tokens, and role-based access control
- [API Reference](api-reference.md) — Complete endpoint reference for all 10 router modules
- [Notifications](notifications.md) — Event-driven notification system
- [Audit Logging](audit-logging.md) — Immutable audit trail for all write operations
- [Deployment Guide](deployment.md) — Docker Compose setup, environment variables, and production configuration
