from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "UPTC Scraping Platform API"
    app_version: str = "0.1.0"
    app_env: str = "development"

    backend_port: int = 8000

    database_url: str = (
        "postgresql+asyncpg://"
        "websec_user:websec_password@postgres:5432/websec"
    )

    qdrant_url: str = "http://qdrant:6333"
    qdrant_collection: str = "analysis_embeddings"

    max_requests_per_second: float = 1.0
    target_timeout_seconds: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()