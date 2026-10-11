from datetime import datetime, timezone

from app.core.models.evidence import Evidence
from app.core.models.finding import Finding
from app.core.models.severity import Severity

from .fingerprint import compute_fingerprint
from ..errors import ResultParseError


def _as_list(value) -> list[str]:
    """El motor entrega a veces listas y a veces strings separados por coma."""
    if value is None:
        return []
    if isinstance(value, str):
        return [x.strip() for x in value.split(",") if x.strip()]
    return [str(x) for x in value]


def _truncate(text: str | None, limit: int) -> str | None:
    if not text:
        return None
    return text if len(text) <= limit else text[:limit] + "\n…[truncado]"


def _parse_timestamp(ts: str | None) -> datetime:
    """El motor emite nanosegundos y la zona horaria local; se normaliza a UTC.

    Si falta o no se puede interpretar, se usa el momento actual.
    """
    if not ts:
        return datetime.now(timezone.utc)
    try:
        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _build_evidence(raw: dict, limit: int) -> Evidence | None:
    """Devuelve la evidencia del hallazgo, o None si el motor no aportó ninguna."""
    request = _truncate(raw.get("request"), limit)
    response = _truncate(raw.get("response"), limit)
    extracted = _as_list(raw.get("extracted-results"))
    if not (request or response or extracted):
        return None
    return Evidence(request=request, response=response, extracted=extracted)


def parse_finding(raw: dict, *, max_evidence_chars: int = 16_384) -> Finding:
    """Convierte un resultado del motor de escaneo en un `Finding`.

    Es el único punto que conoce el formato de salida del motor: las claves
    literales ("template-id", "matched-at"...) pertenecen a ese formato.

    Lanza ResultParseError si el resultado no es interpretable (falta el
    identificador de la regla, tipos inesperados, valores inválidos).
    """
    try:
        return _build_finding(raw, max_evidence_chars)
    except (KeyError, TypeError, AttributeError, ValueError) as e:
        raise ResultParseError(f"Resultado no interpretable: {e!r}") from e


def _build_finding(raw: dict, max_evidence_chars: int) -> Finding:
    info = raw.get("info") or {}
    classification = info.get("classification") or {}

    rule_id = raw["template-id"]
    matched_at = raw.get("matched-at") or raw.get("host") or ""

    try:
        severity = Severity(str(info.get("severity", "unknown")).lower())
    except ValueError:
        severity = Severity.UNKNOWN

    return Finding(
        fingerprint=compute_fingerprint(rule_id, matched_at, raw.get("matcher-name")),
        rule_id=rule_id,
        name=info.get("name") or rule_id,
        severity=severity,
        description=info.get("description"),
        remediation=info.get("remediation"),
        cve_ids=_as_list(classification.get("cve-id")),
        cvss_score=classification.get("cvss-score"),
        host=raw.get("host", ""),
        matched_at=matched_at,
        evidence=_build_evidence(raw, max_evidence_chars),
        detected_at=_parse_timestamp(raw.get("timestamp")),
    )