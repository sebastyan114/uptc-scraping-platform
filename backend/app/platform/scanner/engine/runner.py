import asyncio
import contextlib
import json
import logging
import os
import signal
from collections import deque
from collections.abc import AsyncIterator, Sequence

from app.core.errors import TimeoutExceededError
from ..errors import ScanFailedError

log = logging.getLogger(__name__)

# Máximo por línea de salida (un hallazgo = una línea JSON). El límite por defecto
# de asyncio es 64 KB y los hallazgos con request/response pueden superarlo.
_LINE_LIMIT = 16 * 1024 * 1024

# Únicas variables de entorno que recibe el motor, para que no vea los secretos
# de la aplicación. Sin HOME/XDG_CONFIG_HOME no encuentra su configuración.
_ENV_WHITELIST = ("PATH", "HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "TMPDIR")

_TERM_GRACE_SECONDS = 5.0  # espera tras SIGTERM antes de SIGKILL
_DRAIN_GRACE_SECONDS = 2.0  # espera al cierre de stderr tras terminar el proceso


def _signal_group(proc: asyncio.subprocess.Process, sig: int) -> None:
    try:
        os.killpg(proc.pid, sig)
    except ProcessLookupError:
        pass


def _decode(line: bytes) -> dict | None:
    """Interpreta una línea como objeto JSON; devuelve None si no lo es."""
    try:
        data = json.loads(line)
    except ValueError:  # JSONDecodeError y UnicodeDecodeError
        log.debug("Línea no-JSON ignorada: %r", line[:200])
        return None
    if not isinstance(data, dict):
        log.debug("Línea JSON que no es un objeto, ignorada: %r", line[:200])
        return None
    return data


class EngineRunner:
    """Ejecuta el motor de escaneo como subproceso.

    Emite los resultados a medida que el motor los produce, sin esperar a que termine.
    Solo Unix: termina al motor y a sus hijos mediante grupos de procesos.
    """

    def __init__(self) -> None:
        # Tareas de cierre en curso. asyncio solo guarda referencias débiles a las tareas,
        # así que se retienen aquí hasta que terminen.
        self._shutdowns: set[asyncio.Task] = set()

    async def _finish_shutdown(self, proc: asyncio.subprocess.Process, drain: asyncio.Task) -> None:
        """Completa el cierre del motor: espera su salida y fuerza SIGKILL si no llega a tiempo."""
        try:
            await asyncio.wait_for(proc.wait(), _TERM_GRACE_SECONDS)
        except TimeoutError:
            _signal_group(proc, signal.SIGKILL)
            await proc.wait()
        except asyncio.CancelledError:
            _signal_group(proc, signal.SIGKILL)
            raise
        finally:
            drain.cancel()

    def _schedule_shutdown(self, proc: asyncio.subprocess.Process, drain: asyncio.Task) -> None:
        """Envía SIGTERM y delega el resto del cierre a una tarea en segundo plano.

        Es síncrona a propósito: sin puntos de espera, una cancelación no puede interrumpirla.
        """
        _signal_group(proc, signal.SIGTERM)
        task = asyncio.create_task(self._finish_shutdown(proc, drain))
        self._shutdowns.add(task)
        task.add_done_callback(self._shutdowns.discard)

    async def stream(self, cmd: Sequence[str], timeout: int) -> AsyncIterator[dict]:
        """Lanza `cmd` y emite cada línea JSONL de stdout como dict, en tiempo real.

        `timeout` es un plazo total en segundos, incluido el tiempo que el
        consumidor tarda en procesar cada resultado.

        Lanza:
          TimeoutExceededError     si se supera `timeout`.
          ScanFailedError          si el motor termina con código distinto de 0.

        Ante cualquier salida (éxito, error, timeout, cancelación o consumidor
        que abandona el iterador) el proceso y sus hijos se terminan.
        """

        env = {k: os.environ[k] for k in _ENV_WHITELIST if k in os.environ}
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=_LINE_LIMIT,
            env=env,
            start_new_session=True,  # grupo propio: se puede terminar al motor y a sus hijos
        )
        assert proc.stdout is not None and proc.stderr is not None

        stderr_tail: deque[str] = deque(maxlen=30)

        async def drain_stderr() -> None:
            async for line in proc.stderr:
                stderr_tail.append(line.decode(errors="replace").rstrip())

        drain = asyncio.create_task(drain_stderr())
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        timeout_msg = f"Superado el límite de {timeout}s"

        def remaining() -> float:
            left = deadline - loop.time()
            if left <= 0:
                raise TimeoutExceededError(timeout_msg)
            return left

        try:
            while True:
                left = remaining()
                try:
                    line = await asyncio.wait_for(proc.stdout.readline(), left)
                except TimeoutError:
                    raise TimeoutExceededError(timeout_msg) from None
                except ValueError:
                    log.warning("Línea superior a %d bytes descartada", _LINE_LIMIT)
                    continue

                if not line:  # EOF: el motor cerró stdout
                    break

                result = _decode(line)
                if result is not None:
                    yield result

            if proc.returncode is not None:
                code = proc.returncode
            else:
                try:
                    code = await asyncio.wait_for(proc.wait(), remaining())
                except TimeoutError:
                    raise TimeoutExceededError(timeout_msg) from None

            if code != 0:
                # stderr solo se necesita para el diagnóstico; no se espera en un éxito
                grace = min(_DRAIN_GRACE_SECONDS, max(deadline - loop.time(), 0))
                if grace > 0:
                    with contextlib.suppress(TimeoutError):
                        await asyncio.wait_for(drain, grace)
                raise ScanFailedError(code, "\n".join(stderr_tail))
        finally:
            if proc.returncode is None:
                self._schedule_shutdown(proc, drain)
            else:
                drain.cancel()
