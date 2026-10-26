import time
from typing import Iterator, Callable

from zapv2 import ZAPv2

from app.core.models.enums import TaskStatus
from app.core.models.finding import Finding
from app.core.models.snapshot import Snapshot
from app.core.config import ScannerSettings
from app.scanner.errors import ScanError, translated_errors
from .mappers import to_finding

_POLL_SECONDS = 1


class ScanSession:

    def __init__(self, zap: ZAPv2, target: str, origin: str, *, ctx_name: str, ctx_id: str,
                 settings: ScannerSettings) -> None:
        self._zap = zap
        self._target = target
        self._origin = origin
        self._ctx_name = ctx_name
        self._ctx_id = ctx_id
        self._settings = settings
        self._discovered = False

    @property
    def origin(self) -> str:
        return self._origin

    def discover(self, force=False) -> Iterator[Snapshot[tuple[str, ...]]]:
        if self._discovered and not force:
            return

        with translated_errors():
            zap = self._zap
            task = zap.spider.scan(self._target, contextname=self._ctx_name, recurse="true")
            yield from self._stream(
                lambda: tuple(sorted(zap.core.urls(baseurl=self._origin))),
                lambda: int(zap.spider.status(task)) >= 100,
                timeout=self._settings.discovery_seconds,
                stop=lambda: zap.spider.stop(task),
            )
            self._discovered = True

    def analyze(self) -> Iterator[Snapshot[tuple[Finding, ...]]]:
        self._require_discovered()

        active_scan = self._settings.active_scan_enabled

        with translated_errors():
            zap = self._zap
            task = zap.ascan.scan(self._target, recurse="true", contextid=self._ctx_id) if active_scan else None

            def is_done() -> bool:
                if task is not None and int(zap.ascan.status(task)) < 100:
                    return False
                return int(zap.pscan.records_to_scan) == 0

            def stop() -> None:
                if task is not None:
                    zap.ascan.stop(task)
                zap.pscan.clear_queue()

            yield from self._stream(
                self._findings,
                is_done,
                timeout=self._settings.analysis_seconds,
                stop=stop,
            )

    def _findings(self) -> tuple[Finding, ...]:
        return tuple(to_finding(a) for a in self._zap.core.alerts(baseurl=self._origin))

    def _require_discovered(self) -> None:
        if not self._discovered:
            raise ScanError("Primero hay que explorar el sitio.")

    @staticmethod
    def _stream[T](
            read_data: Callable[[], T],
            is_done: Callable[[], bool],
            *,
            timeout: float,
            stop: Callable[[], None] = lambda: None,
    ) -> Iterator[Snapshot[T]]:
        deadline = time.monotonic() + timeout
        last: Snapshot[T] | None = None
        while True:
            done = is_done()
            snap = Snapshot(data=read_data(), status=TaskStatus.FINISHED if done else TaskStatus.RUNNING)
            if snap != last:
                last = snap
                yield snap
            if done:
                return
            if time.monotonic() >= deadline:
                stop()
                yield Snapshot(data=read_data(), status=TaskStatus.TIMED_OUT)
                return
            time.sleep(_POLL_SECONDS)
