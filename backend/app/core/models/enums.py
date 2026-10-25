from enum import StrEnum


class Risk(StrEnum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Informational"

    @property
    def rank(self) -> int:
        return _RISK_RANK[self]


_RISK_RANK = {Risk.HIGH: 0, Risk.MEDIUM: 1, Risk.LOW: 2, Risk.INFO: 3}


class Confidence(StrEnum):
    FALSE_POSITIVE = "False Positive"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CONFIRMED = "Confirmed"
