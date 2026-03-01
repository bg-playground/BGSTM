import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    analytics,
    audit_log,
    auth,
    links,
    notifications,
    requirements,
    suggestions,
    test_cases,
    traceability,
    users,
)
from app.config import settings
from app.db.session import init_db

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, description="BGSTM AI-Powered Traceability System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["auth"])
app.include_router(requirements.router, prefix=settings.API_V1_PREFIX, tags=["requirements"])
app.include_router(test_cases.router, prefix=settings.API_V1_PREFIX, tags=["test_cases"])
app.include_router(links.router, prefix=settings.API_V1_PREFIX, tags=["links"])
app.include_router(suggestions.router, prefix=settings.API_V1_PREFIX, tags=["suggestions"])
app.include_router(traceability.router, prefix=settings.API_V1_PREFIX, tags=["traceability"])
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX, tags=["analytics"])
app.include_router(audit_log.router, prefix=settings.API_V1_PREFIX, tags=["audit_log"])
app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["users"])
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX, tags=["notifications"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup (only for non-PostgreSQL, e.g. SQLite in tests)."""
    if not settings.DATABASE_URL.startswith("postgresql"):
        await init_db()

    # Seed default admin user if no users exist
    # WARNING: Change the default password on first use in production!
    from app.auth.security import get_password_hash
    from app.crud.user import get_user_by_email
    from app.db.session import AsyncSessionLocal
    from app.models.user import User, UserRole

    default_email = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@bgstm.local")
    default_password = os.environ.get("DEFAULT_ADMIN_PASSWORD", "admin1234")

    async with AsyncSessionLocal() as db:
        existing = await get_user_by_email(db, default_email)
        if not existing:
            db.add(
                User(
                    email=default_email,
                    hashed_password=get_password_hash(default_password),
                    full_name="Default Admin",
                    role=UserRole.admin,
                )
            )
            await db.commit()


@app.get("/")
async def root():
    return {"message": "BGSTM AI Traceability API", "version": settings.VERSION, "docs": "/docs"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
