"""Application settings, loaded from environment variables / .env file."""
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # App
    APP_NAME: str = "Lumini"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/job_agent"
    )
    DATABASE_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT / Auth
    JWT_SECRET_KEY: str = "change-me-in-production-please"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # LLM / LiteLLM
    # LLM_DEFAULT_MODEL uses LiteLLM's provider-prefixed model naming, e.g.
    # "claude-sonnet-5" (Anthropic direct), "openrouter/openai/gpt-oss-20b:free"
    # (via OpenRouter), "gpt-4o-mini" (OpenAI direct). app/llm/client.py picks the
    # matching API key below from the model's prefix automatically. Defaults to
    # a free OpenRouter model so the app works out of the box with just an
    # OPENROUTER_API_KEY and no paid provider key required.
    LLM_PROVIDER: str = "openrouter"
    LLM_DEFAULT_MODEL: str = "openrouter/openai/gpt-oss-20b:free"
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS: int = 1536

    # File storage — local disk by default; set CLOUDINARY_URL
    # (cloudinary://<api_key>:<api_secret>@<cloud_name>) to store resumes in
    # Cloudinary instead. See app/services/storage_service.py.
    CLOUDINARY_URL: str = ""
    RESUME_STORAGE_DIR: str = "./storage/resumes"
    SCREENSHOT_STORAGE_DIR: str = "./storage/screenshots"
    MAX_UPLOAD_SIZE_MB: int = 10

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # LangGraph checkpointing
    CHECKPOINT_DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/job_agent"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
