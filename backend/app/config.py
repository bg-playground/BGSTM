from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./bgstm.db"
    # For PostgreSQL: "postgresql+asyncpg://user:password@localhost/bgstm"

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "BGSTM AI Traceability"
    VERSION: str = "2.0.0"

    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]

    # Auto-Suggestions
    AUTO_SUGGESTIONS_ENABLED: bool = True
    AUTO_SUGGESTIONS_ALGORITHM: str = "tfidf"  # 'tfidf', 'keyword', or 'hybrid'
    AUTO_SUGGESTIONS_THRESHOLD: float = 0.3  # Minimum confidence threshold (0.0-1.0)

    # Authentication
    SECRET_KEY: str = "change-me-in-production-use-a-real-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # Storage (artifact uploads — BGSTM#298)
    STORAGE_BACKEND: Literal["local", "s3"] = "local"
    STORAGE_LOCAL_ROOT: Path = Path("./var/artifacts")
    STORAGE_LOCAL_PUBLIC_BASE_URL: str = "http://localhost:8000/artifacts"
    STORAGE_MAX_UPLOAD_BYTES: int = 52_428_800  # 50 MB
    STORAGE_ALLOWED_CONTENT_TYPES: list[str] = [
        "image/png",
        "image/jpeg",
        "video/mp4",
        "video/webm",
        "application/zip",
        "text/plain",
        "application/json",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
