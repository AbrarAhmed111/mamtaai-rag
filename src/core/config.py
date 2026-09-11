"""
Application Configuration
Centralized settings loaded from environment variables using Pydantic Settings.
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Core application settings."""
    APP_NAME: str = "MumtaAI Chatbot API"
    ENVIRONMENT: str = "development"
    API_VERSION: str = "1.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: str = "*"

    # Gateway Default Settings
    GATEWAY_MAX_ATTEMPTS: int = 5
    GATEWAY_COOLDOWN_SECONDS: int = 60

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
