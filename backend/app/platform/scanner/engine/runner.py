import asyncio
import contextlib
import json
import logging
import os
import shutil
import signal
from collections.abc import AsyncIterator, Sequence
from collections import deque

from ..errors import EngineNotFound, ScanFailed, ScanTimeout

log = logging.getLogger(__name__)

# Máximo por línea de salida (un hallazgo = una línea JSON). El límite por defecto
# de asyncio es 64 KB y los hallazgos con request/response pueden superarlo.
_LINE_LIMIT = 16 * 1024 * 1024

# Únicas variables de entorno que recibe el motor, para que no vea los secretos
# de la aplicación. Sin HOME/XDG_CONFIG_HOME no encuentra su configuración.
_ENV_WHITELIST = ("PATH", "HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "TMPDIR")

_TERM_GRACE_SECONDS = 5  # espera tras SIGTERM antes de SIGKILL
_DRAIN_GRACE_SECONDS = 2  # espera al cierre de stderr tras terminar el proceso


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

    async def stream(self, cmd: Sequence[str], timeout: int) -> AsyncIterator[dict]:
        """Lanza `cmd` y emite cada línea JSONL de stdout como dict, en tiempo real.

        `timeout` es un plazo total en segundos, incluido el tiempo que el
        consumidor tarda en procesar cada resultado.

        Lanza:
          EngineNotFound  si el binario no existe.
          ScanTimeout     si se supera `timeout`.
          ScanFailed      si el motor termina con código distinto de 0.

        Ante cualquier salida (éxito, error, timeout, cancelación o consumidor
        que abandona el iterador) el proceso y sus hijos se terminan.
        """
        binary, *args = cmd
        if shutil.which(binary) is None:
            raise EngineNotFound(f"No se encuentra el binario: {binary}")

        env = {k: os.environ[k] for k in _ENV_WHITELIST if k in os.environ}
        proc = await asyncio.create_subprocess_exec(
            binary,*args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=_LINE_LIMIT,
            env=env,
            start_new_session=True,  # grupo propio: se puede terminar al motor y a sus hijos
        )
        assert proc.stdout is not None and proc.stderr is not None

        # stderr se lee siempre en una tarea aparte: si el pipe se llena, el motor se
        # bloquea al escribir. Solo se conservan las últimas 30 líneas, para diagnosticar fallos.
        stderr_tail: deque[str] = deque(maxlen=30)

        async def drain_stderr() -> None:
            async for line in proc.stderr:
                stderr_tail.append(line.decode(errors="replace").rstrip())

        drain = asyncio.create_task(drain_stderr())
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        timeout_msg = f"Superado el límite de {timeout}s"

        def time_left() -> float:
            return max(deadline - loop.time(), 0)

        try:
            while True:
                try:
                    line = await asyncio.wait_for(proc.stdout.readline(), time_left())
                except TimeoutError:
                    raise ScanTimeout(timeout_msg) from None
                except ValueError:
                    log.warning("Línea superior a %d bytes descartada", _LINE_LIMIT)
                    continue

                if not line:  # EOF: el motor cerró stdout
                    break
                result = _decode(line)
                if result is not None:
                    yield result

            try:
                code = await asyncio.wait_for(proc.wait(), time_left())
            except TimeoutError:
                raise ScanTimeout(timeout_msg) from None

            # Un proceso hijo puede mantener stderr abierto: no esperar indefinidamente
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(drain, _DRAIN_GRACE_SECONDS)

            if code != 0:
                raise ScanFailed(code, "\n".join(stderr_tail))
        finally:
            if proc.returncode is None:
                # Cierre en dos fases: SIGTERM permite al motor terminar de forma ordenada;
                # si no responde en _TERM_GRACE_SECONDS, SIGKILL lo fuerza.
                _signal_group(proc, signal.SIGTERM)
                try:
                    await asyncio.wait_for(proc.wait(), _TERM_GRACE_SECONDS)
                except TimeoutError:
                    _signal_group(proc, signal.SIGKILL)
                    await proc.wait()
            drain.cancel()
