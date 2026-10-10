from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Prueba técnica de un hallazgo.

    Va separada de `Finding` porque es pesada y puede contener datos sensibles
    del objetivo (cookies, tokens, datos personales).
    """

    request: str | None = None
    """Petición que provocó el hallazgo."""

    response: str | None = None
    """Respuesta del servidor."""

    extracted: list[str] = Field(default_factory=list)
    """Valores concretos que se obtuvieron como prueba de la vulnerabilidad."""
