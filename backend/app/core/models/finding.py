from dataclasses import dataclass

from .enums import Risk, Confidence


@dataclass(frozen=True, slots=True, kw_only=True)
class Finding:

    alert_ref: str
    name: str
    risk: Risk
    confidence: Confidence
    description: str
    solution: str | None = None
    cwe: int | None = None

    url: str
    method: str | None = None
    param: str | None = None
    attack: str | None = None
    evidence: str | None = None

    additional_info: str | None = None
    references: tuple[str, ...] = ()
