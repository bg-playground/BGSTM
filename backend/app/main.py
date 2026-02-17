from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.session import init_db
from app.api import requirements, test_cases, links, suggestions

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="BGSTM AI-Powered Traceability System"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(requirements.router, prefix=settings.API_V1_PREFIX, tags=["requirements"])
app.include_router(test_cases.router, prefix=settings.API_V1_PREFIX, tags=["test_cases"])
app.include_router(links.router, prefix=settings.API_V1_PREFIX, tags=["links"])
app.include_router(suggestions.router, prefix=settings.API_V1_PREFIX, tags=["suggestions"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()


@app.get("/")
async def root():
    return {
        "message": "BGSTM AI Traceability API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
