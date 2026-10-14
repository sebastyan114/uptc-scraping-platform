import logging
from collections.abc import AsyncIterator, Sequence

from app.core.config import ScannerSettings
from app.core.errors import InvalidTargetError
from app.core.models import Finding
from app.core.target_validation import validate_target
from .engine.command import build_command
from .engine.parser import parse_finding
from .engine.runner import EngineRunner
from .errors import ResultParseError

log = logging.getLogger(__name__)


class ScannerService:
    """Escanea objetivos web en busca de vulnerabilidades mediante el motor de escaneo."""

    def __init__(self, settings: ScannerSettings, runner: EngineRunner) -> None:
        self._settings = settings
        self._runner = runner

    async def scan(self, targets: Sequence[str]) -> AsyncIterator[Finding]:
        """Escanea todos los objetivos en una sola ejecución del motor.

        Los objetivos se validan antes de empezar y el motor los procesa en
        paralelo. Cada hallazgo se emite en cuanto el motor lo produce. Un
        hallazgo repetido (mismo fingerprint) se emite una sola vez.

        Lanza:
          InvalidTargetError    si hay demasiados objetivos o ninguno es válido.
          ScanFailedError       si el motor termina con error.
          TimeoutExceededError  si se supera `scan_timeout_seconds`.
        Los dos últimos abortan el escaneo; los hallazgos ya emitidos se conservan.
        """
        valid_targets = self._validated_targets(targets)
        limit = self._settings.max_scan_seconds
        log.info("escaneo iniciado: objetivos=%d", len(valid_targets))

        seen: set[str] = set()
        cmd = build_command(
            binary=self._settings.engine_bin,
            targets=valid_targets, max_scan_seconds=limit,
            request_timeout_seconds=self._settings.request_timeout_seconds
        )

        log.debug("ejecutando comando: %s", " ".join(cmd))

        async for raw in self._runner.stream(cmd, timeout=limit):
            try:
                finding = parse_finding(
                    raw, max_evidence_chars=self._settings.max_evidence_chars
                )
            except ResultParseError as e:
                log.warning("resultado descartado: %s", e)
                continue

            if finding.fingerprint in seen:
                continue
            seen.add(finding.fingerprint)
            yield finding

    def _validated_targets(self, targets: Sequence[str]) -> list[str]:
        """Devuelve los objetivos permitidos, sin duplicados y en el orden original."""
        unique = list(dict.fromkeys(t.strip() for t in targets))
        if len(unique) > self._settings.max_targets:
            raise InvalidTargetError(
                f"Demasiados objetivos ({len(unique)} > {self._settings.max_targets})"
            )

        valid: list[str] = []
        for target in unique:
            try:
                valid.append(
                    validate_target(target, allow_private=self._settings.allow_private_targets)
                )
            except InvalidTargetError as e:
                log.warning("objetivo rechazado: %s", e)

        if not valid:
            raise InvalidTargetError("Ningún objetivo superó la validación")
        return valid
