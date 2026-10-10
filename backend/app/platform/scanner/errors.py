from secplatform.core.errors import ExecutionTimeout, PlatformError


class ScanError(PlatformError):
    """Errores propios del módulo scanner."""


class EngineNotFound(ScanError):
    """El binario del motor no existe o no es ejecutable. Error de despliegue: no reintentar."""


class ScanFailed(ScanError):
    """El motor terminó con código de salida distinto de 0.

    `detail` contiene las últimas líneas de stderr, solo para logs.
    No exponerlo en respuestas de API.
    """

    def __init__(self, code: int, detail: str = ""):
        super().__init__(f"El escaneo terminó con código {code}")
        self.code = code
        self.detail = detail


class ScanTimeout(ScanError, ExecutionTimeout):
    """Se superó el tiempo máximo por objetivo. Los hallazgos previos ya fueron entregados."""