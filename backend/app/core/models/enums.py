from enum import StrEnum


class Risk(StrEnum):
    UNKNOWN = "Unknown"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Informational"

    @property
    def rank(self) -> int:
        return _RISK_RANK[self]


_RISK_RANK = {Risk.HIGH: 0, Risk.MEDIUM: 1, Risk.LOW: 2, Risk.INFO: 3, Risk.UNKNOWN: 99}


class Confidence(StrEnum):
    UNKNOWN = "Unknown"
    FALSE_POSITIVE = "False Positive"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CONFIRMED = "Confirmed"


class TaskStatus(StrEnum):
    RUNNING = "running"      # la etapa sigue en curso: `data` es parcial
    FINISHED = "finished"    # terminó con normalidad: `data` es definitivo
    TIMED_OUT = "timed_out"  # se cortó por tiempo: `data` es definitivo pero puede estar incompleto