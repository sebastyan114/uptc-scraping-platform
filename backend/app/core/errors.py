class AppError(Exception):
    """Base de los errores esperados de la aplicación."""


class ScopeViolation(AppError):
    """El objetivo no está permitido: IP no pública, esquema inválido,
    host que no resuelve, credenciales en la URL o demasiados objetivos."""


class ExecutionTimeout(AppError):
    """Una ejecución superó su tiempo máximo."""