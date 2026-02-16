from pydantic_settings import BaseSettings
from typing import Optional


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
    
    class Config:
        env_file = ".env"


settings = Settings()
