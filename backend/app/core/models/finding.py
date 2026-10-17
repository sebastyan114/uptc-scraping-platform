from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class Risk(StrEnum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Informational"


RISK_RANK = {Risk.HIGH: 0, Risk.MEDIUM: 1, Risk.LOW: 2, Risk.INFO: 3}


class Confidence(StrEnum):
    FALSE_POSITIVE = "False Positive"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CONFIRMED = "Confirmed"


class Finding(BaseModel):
    model_config = ConfigDict(frozen=True)

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
    references: list[str] = []
