import ipaddress
import re
from urllib.parse import urlsplit

from app.core.errors import InvalidTargetError

_MAX_LENGTH = 2048
_INVALID_CHARS = re.compile(r"[\s\x00-\x1f]")  # espacios y caracteres de control
_ALLOWED_SCHEMES = ("", "http", "https")
_INTERNAL_SUFFIXES = (".localhost", ".local", ".internal")

# IPs en formatos no estándar ("2130706433", "0x7f.1", "0177.0.0.1") que algunos
# resolvers aceptan y equivalen a 127.0.0.1. ipaddress no las reconoce.
_NUMERIC_HOST = re.compile(r"^(0x[0-9a-f]+|\d+)(\.(0x[0-9a-f]+|\d+))*$", re.IGNORECASE)


def _is_public(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Indica si la IP es enrutable públicamente (no privada, loopback, link-local ni CGNAT)."""
    if ip.version == 6 and ip.ipv4_mapped:  # ::ffff:127.0.0.1 es en realidad IPv4
        ip = ip.ipv4_mapped
    return ip.is_global


def _extract_host(target: str) -> str:
    """Valida la forma y la política de esquema y credenciales; devuelve el host.

    Lanza InvalidTargetError si está mal formado y TargetNotAllowedError si el
    esquema o las credenciales no están permitidos.
    """
    if (
            not target
            or len(target) > _MAX_LENGTH
            or _INVALID_CHARS.search(target)
            or target.startswith("-")  # evita que se interprete como un flag del motor
    ):
        raise InvalidTargetError("Objetivo inválido")

    try:
        parts = urlsplit(target if "://" in target else f"//{target}")
        _ = parts.port  # valida el rango; lanza ValueError si es inválido
    except ValueError as e:
        raise InvalidTargetError("Objetivo malformado") from e

    if not parts.hostname:
        raise InvalidTargetError("El objetivo no tiene host")
    if parts.scheme not in _ALLOWED_SCHEMES:
        raise InvalidTargetError(f"Esquema no permitido: {parts.scheme}")
    if parts.username or parts.password:
        raise InvalidTargetError("No se permiten credenciales en la URL")
    return parts.hostname


def _check_host(host: str) -> None:
    """Rechaza hosts internos reconocibles por su forma, sin resolver DNS."""
    name = host.lower().rstrip(".")
    if name == "localhost" or name.endswith(_INTERNAL_SUFFIXES):
        raise InvalidTargetError("Host interno no permitido")

    try:
        ip = ipaddress.ip_address(name.split("%")[0])  # quita el scope id de IPv6
    except ValueError:
        if _NUMERIC_HOST.match(name):
            raise InvalidTargetError("Dirección IP en formato no estándar") from None
        return  # nombre de dominio normal

    if not _is_public(ip):
        raise InvalidTargetError(f"IP no pública: {ip}")


def validate_target(target: str, *, allow_private: bool = False) -> str:
    """Valida un objetivo y lo devuelve sin espacios en los extremos.

    Solo se permiten URLs http/https sin credenciales, y se rechazan las IPs no
    públicas y los hosts internos evidentes (localhost, *.local, *.internal).
    No resuelve DNS: la protección frente a dominios que apuntan a IPs internas
    y a redirecciones debe hacerse filtrando el egress de red del worker.

    `allow_private` omite la comprobación de host (solo para laboratorio).

    Lanza:
      InvalidTargetError     si está mal formado o la política no lo permite.
    """
    target = target.strip()
    host = _extract_host(target)
    if not allow_private:
        _check_host(host)
    return target
