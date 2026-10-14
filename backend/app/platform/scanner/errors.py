from app.core.errors import AppError


class ScanFailedError(AppError):
    """El motor terminó con código de salida distinto de 0.

    `detail` contiene las últimas líneas de stderr, solo para logs.
    No exponerlo en respuestas de API.
    """

    def __init__(self, code: int, detail: str = ""):
        super().__init__(f"El escaneo terminó con código {code}")
        self.code = code
        self.detail = detail


class ResultParseError(AppError):
    """Un resultado del motor no se pudo parsear correctamente."""
