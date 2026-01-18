"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://mongodb:27017/intelligence"

    # LLM Service Configuration
    LLM_SERVICE_URL: str = "http://llm:11434"
    LLM_MODEL: str = "llama3"

    # Backend Configuration
    BACKEND_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Scraper Configuration
    SCRAPER_MAX_ARTICLES: int = 100
    SCRAPER_TIMEOUT: int = 30

    # Analyzer Configuration
    ANALYZER_TIMEOUT: int = 30
    ANALYZER_MAX_CONTENT_LENGTH: int = 10000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Global settings instance
settings = Settings()
