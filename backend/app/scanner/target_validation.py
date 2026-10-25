from __future__ import annotations

import ipaddress
import logging
import re

from urllib.parse import urlsplit

from app.scanner.errors import TargetError

log = logging.getLogger(__name__)

_MAX_LENGTH = 2048
_INVALID_CHARS = re.compile(r"[\s\x00-\x1f\x7f\\]")  # espacios, control y backslash (los parsers lo tratan distinto)
_HAS_SCHEME = re.compile(r"^[a-z][a-z0-9+.\-]*://", re.IGNORECASE)
_DEFAULT_SCHEME = "https"
_ALLOWED_SCHEMES = ("http", "https")

_INTERNAL_SUFFIXES = (".localhost", ".localdomain", ".local", ".internal", ".lan", ".home.arpa", ".corp", ".intranet")
_DOMAIN = re.compile(r"[a-z0-9_-]+(\.[a-z0-9_-]+)*")

# IPs en formatos no estándar ("2130706433", "0x7f.1", "0177.0.0.1", "127.1") que algunos
# resolvers aceptan y equivalen a 127.0.0.1. `ipaddress` no las reconoce.
_NUMERIC_HOST = re.compile(r"(0x[0-9a-f]+|\d+)(\.(0x[0-9a-f]+|\d+))*", re.IGNORECASE)

_NAT64 = ipaddress.ip_network("64:ff9b::/96")  # traduce a IPv4 arbitrarias en redes con NAT64


def validate_target(target: str, *, allow_private: bool = False) -> str:
    """Valida un objetivo y lo devuelve normalizado (sin espacios y con esquema).

    Solo se permiten URLs http/https sin credenciales. Si falta el esquema se añade
    `https://`. Con `allow_private` se omite la comprobación del host.

    Lanza:
      InvalidTargetError      si está mal formado.
      TargetNotAllowedError   si la política no lo permite.
    """
    candidate, host = _split(target.strip())
    if not allow_private:
        _check_host(host)
    return candidate


def _split(target: str) -> tuple[str, str]:
    """Valida la forma, el esquema y las credenciales. Devuelve (URL normalizada, host)."""
    if not target or len(target) > _MAX_LENGTH or _INVALID_CHARS.search(target):
        raise TargetError("La URL no es válida.")

    candidate = target if _HAS_SCHEME.match(target) else f"{_DEFAULT_SCHEME}://{target}"
    try:
        parts = urlsplit(candidate)
        _ = parts.port  # fuerza la validación del puerto
        host = parts.hostname
    except ValueError as exc:
        raise TargetError("La URL no es válida.") from exc

    if not host:
        raise TargetError("La URL no tiene host.")
    if parts.scheme not in _ALLOWED_SCHEMES:
        raise TargetError("Solo se permiten URLs http y https.")
    if "@" in parts.netloc:
        raise TargetError("No se permiten credenciales en la URL.")
    return candidate, host


def _check_host(host: str) -> None:
    """Rechaza hosts internos reconocibles por su forma, sin resolver DNS."""
    name = _normalize(host)

    try:
        ip = ipaddress.ip_address(name.split("%")[0])
    except ValueError:
        pass
    else:
        if not _is_public(ip):
            raise _not_allowed(host, "La dirección del objetivo no está permitida.")
        return

    if not _DOMAIN.fullmatch(name):
        raise TargetError("El nombre del host no es válido.")
    if _NUMERIC_HOST.fullmatch(name):
        raise _not_allowed(host, "La dirección del objetivo no está permitida.")
    if "." not in name or name.endswith(_INTERNAL_SUFFIXES):
        raise _not_allowed(host, "El host del objetivo no está permitido.")


def _normalize(host: str) -> str:
    try:
        return host.lower().rstrip(".").encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise TargetError("El nombre del host no es válido.") from exc


def _is_public(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Indica si la IP es enrutable públicamente (no privada, loopback, link-local ni CGNAT)."""
    if ip.version == 6:
        if ip.ipv4_mapped:  # ::ffff:127.0.0.1 es en realidad IPv4
            ip = ip.ipv4_mapped
        elif ip in _NAT64:
            return False
    return ip.is_global


def _not_allowed(host: str, message: str) -> TargetError:
    log.warning("Objetivo rechazado: host=%r motivo=%s", host, message)
    return TargetError(message)