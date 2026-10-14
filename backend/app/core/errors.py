class AppError(Exception):
    """Base de los errores esperados de la aplicación."""


class TimeoutExceededError(AppError):
    """Una ejecución superó su tiempo máximo."""


class InvalidTargetError(AppError):
    """El objetivo no es válido: está mal formado o la política no lo permite."""
