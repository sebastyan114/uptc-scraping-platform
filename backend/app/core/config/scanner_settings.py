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

    discovery_max_depth: int = Field(default=5, ge=1)
    discovery_seconds: float = Field(default=40.0, ge=20, allow_inf_nan=False)
    analysis_seconds: float = Field(default=80.0, ge=40, allow_inf_nan=False)
    active_scan_enabled: bool = False
    request_timeout_seconds: int = Field(10, gt=0)

    # Solo laboratorio. Seguro por defecto: los objetivos internos se rechazan.
    allow_private_targets: bool = False



@lru_cache
def get_scanner_settings() -> ScannerSettings:
    return ScannerSettings()  # type: ignore[call-arg]
