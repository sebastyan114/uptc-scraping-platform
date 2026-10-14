from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    app_name: str = "Name"
    app_version: str = "0.1.0"
    app_env: Literal["development", "staging", "production"] = "development"
    app_port: int = Field(8000, ge=1, le=65535)

    database_url: SecretStr
    qdrant_url: str
    qdrant_collection: str = "analysis_embeddings"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
