from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator

from app.core.models.evidence import Evidence
from app.core.models.severity import Severity


class Finding(BaseModel):
    """Vulnerabilidad detectada en un objetivo.

    Atributos:
        fingerprint:  Identificador estable del hallazgo entre ejecuciones. Sirve para
                      deduplicar y comparar scans (nuevo, persistente, resuelto).
        rule_id:      Identificador de la regla que lo detectó.
        name:         Título legible de la vulnerabilidad.
        severity:     Nivel de gravedad.
        description:  Explicación de la vulnerabilidad.
        remediation:  Cómo corregirla.
        cve_ids:      CVEs asociados, normalizados a mayúsculas. Puede estar vacío.
        cvss_score:   Puntuación CVSS (0.0 a 10.0), si existe.
        host:         Host afectado.
        matched_at:   URL exacta donde se detectó.
        evidence:     Prueba técnica, opcional (ver `Evidence`).
        detected_at:  Momento de la detección, en UTC.
    """

    fingerprint: str
    rule_id: str

    name: str
    severity: Severity
    description: str | None = None
    remediation: str | None = None
    cve_ids: list[str] = Field(default_factory=list)
    cvss_score: float | None = None

    host: str
    matched_at: str

    evidence: Evidence | None = None
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("cve_ids")
    @classmethod
    def _uppercase_cves(cls, v: list[str]) -> list[str]:
        """Normaliza los IDs a mayúsculas, sin importar la fuente."""
        return [x.upper() for x in v]