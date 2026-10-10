from enum import StrEnum


class Severity(StrEnum):
    """Gravedad de un hallazgo, de menor a mayor: info, low, medium, high, critical.

    `unknown` es un valor de respaldo cuando no se reconoce el nivel.
    Para ordenar por gravedad usa `rank`: el orden alfabético del string no sirve.
    """

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

    @property
    def rank(self) -> int:
        """Posición numérica (unknown=-1 ... critical=4) para ordenar y comparar."""
        return _RANK[self]


_RANK = {
    Severity.UNKNOWN: -1, Severity.INFO: 0, Severity.LOW:      1,
    Severity.MEDIUM:   2, Severity.HIGH: 3, Severity.CRITICAL: 4,
}