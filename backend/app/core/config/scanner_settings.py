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
    discovery_share: float = Field(default=0.33, ge=0.15, lt=0.5)
    max_duration_seconds: float = Field(default=120.0, ge=60, allow_inf_nan=False)
    active_scan_enabled: bool = False

    request_timeout_seconds: int = Field(10, gt=0)

    # Solo laboratorio. Seguro por defecto: los objetivos internos se rechazan.
    allow_private_targets: bool = False

    @property
    def discovery_seconds(self) -> float:
        return self.max_duration_seconds * self.discovery_share

    @property
    def analysis_seconds(self) -> float:
        return self.max_duration_seconds - self.discovery_seconds



@lru_cache
def get_scanner_settings() -> ScannerSettings:
    return ScannerSettings()  # type: ignore[call-arg]
