from app.core.errors import AppError


class ScanError(AppError):
    """Base de todos los errores del motor."""


class TargetUnreachable(ScanError):
    """El objetivo no responde o tardó demasiado."""


class TargetError(ScanError):
    """Problema con la URL del usuario: mal formada, no permitida, inalcanzable..."""