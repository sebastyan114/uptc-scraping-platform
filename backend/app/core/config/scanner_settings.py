from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ScannerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SCANNER_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    engine_bin: str = "nuclei"
    max_scan_seconds: int = Field(60, gt=0)
    request_timeout_seconds: int = Field(10, gt=0)
    max_targets: int = Field(50, gt=0)
    max_evidence_chars: int = Field(16_384, gt=0)

    # Solo laboratorio. Seguro por defecto: los objetivos internos se rechazan.
    allow_private_targets: bool = False


@lru_cache
def get_scanner_settings() -> ScannerSettings:
    return ScannerSettings() # type: ignore[call-arg]