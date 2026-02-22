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

    class Config:
        env_file = ".env"


settings = Settings()
