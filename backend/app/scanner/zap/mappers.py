from __future__ import annotations

import logging

from app.core.models.enums import Confidence, Risk
from app.core.models.finding import Finding

log = logging.getLogger(__name__)

_RISK = {
    "informational": Risk.INFO,
    "low": Risk.LOW,
    "medium": Risk.MEDIUM,
    "high": Risk.HIGH,
}
_CONFIDENCE = {
    "low": Confidence.LOW,
    "medium": Confidence.MEDIUM,
    "high": Confidence.HIGH,
}


def to_finding(alert: dict) -> Finding:
    return Finding(
        alert_ref=_text(alert.get("alertRef")) or "",
        name=_text(alert.get("alert") or alert.get("name")) or "",
        risk=_lookup(_RISK, alert.get("risk"), Risk.UNKNOWN),
        confidence=_lookup(_CONFIDENCE, alert.get("confidence"), Confidence.UNKNOWN),
        description=_text(alert.get("description")) or "",
        solution=_text(alert.get("solution")),
        cwe=_cwe(alert.get("cweid")),
        url=_text(alert.get("url")) or "",
        method=_text(alert.get("method")),
        param=_text(alert.get("param")),
        attack=_text(alert.get("attack")),
        evidence=_text(alert.get("evidence")),
        additional_info=_text(alert.get("other")),
        references=tuple((_text(alert.get("reference")) or "").split()),
    )


def _text(value: object) -> str | None:
    if value is None:
        return None
    return str(value).strip() or None


def _cwe(value: object) -> int | None:
    try:
        number = int(str(value))
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _lookup[E](table: dict[str, E], value: object, default: E) -> E:
    found = table.get((_text(value) or "").lower())
    if found is None:
        return default
    return found