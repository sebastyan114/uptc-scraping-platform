import logging
from contextlib import contextmanager
from typing import Iterator

log = logging.getLogger(__name__)


class ScanError(Exception):
    """Base de todos los errores del motor."""


class TargetUnreachable(ScanError):
    """El objetivo no responde o tardó demasiado."""


class TargetError(ScanError):
    """Problema con la URL del usuario: mal formada, no permitida, inalcanzable..."""


@contextmanager
def translated_errors() -> Iterator[None]:
    try:
        yield
    except ScanError:
        raise
    except Exception as exc:
        log.exception("Fallo inesperado durante el escaneo")
        raise ScanError("Ha ocurrido un error inesperado...") from exc
