"""
Application Configuration
Centralized settings loaded from environment variables using Pydantic Settings.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "LLM FastAPI Backend"
    ENVIRONMENT: str = "development"
    API_VERSION: str = "1.0.0"
    PORT: int = 8000
    BASE_URL: str = "http://localhost:8000"
    
    # CORS Configuration (comma-separated origins or '*' for all)
    ALLOWED_ORIGINS: str = "*"
    
    # LLM Configuration
    # Universal OpenAI-compatible interface: works with OpenAI, Groq, DeepSeek, Ollama, OpenRouter, etc.
    LLM_API_KEY: str = "dummy-key-for-local"
    LLM_BASE_URL: Optional[str] = None  # None uses official OpenAI API; customize for Groq, Ollama, etc.
    LLM_DEFAULT_MODEL: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: Optional[int] = 2048
    
    # Embedding Configuration
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into a list."""
        if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
