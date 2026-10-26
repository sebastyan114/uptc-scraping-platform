from __future__ import annotations

import logging
import math
import re
import threading
from contextlib import contextmanager
from typing import Iterator
from urllib.parse import urlsplit, urljoin

import requests
from requests.adapters import HTTPAdapter
from zapv2 import ZAPv2

from app.core.config import ScannerSettings
from app.scanner.errors import ScanError, TargetError, translated_errors
from app.scanner.target_validation import validate_target
from .session import ScanSession

log = logging.getLogger(__name__)

_CONTEXT_NAME = "scan"
_DISCOVERY_WORKERS = 4
_DISCOVERY_EXCLUDE_PATTERN = "(?i).*(logout|logoff|signout|delete|remove).*"  # rutas destructivas
_DISCOVERY_FORMS_ENABLED = False
_MAX_REDIRECTS = 5

_CONNECT_TIMEOUT = 3.0
_API_READ_TIMEOUT = 6.0
_READ_GRACE = 3.0

_timeout_installed = False


def install_api_timeout() -> None:
    global _timeout_installed
    if _timeout_installed:
        return
    original_send = HTTPAdapter.send
    timeout = (_CONNECT_TIMEOUT, _API_READ_TIMEOUT)

    api_url_base = urlsplit(ZAPv2.base)
    def send(self, request, **kwargs):
        target = urlsplit(request.url)
        if (
                kwargs.get("timeout") is None
                and target.scheme == api_url_base.scheme
                and target.netloc == api_url_base.netloc
        ):
            kwargs["timeout"] = timeout
        return original_send(self, request, **kwargs)

    HTTPAdapter.send = send
    _timeout_installed = True


class ScanEngine:
    def __init__(self, proxy: str, api_key: str, settings: ScannerSettings) -> None:
        install_api_timeout()
        self._proxies = {"http": proxy, "https": proxy}
        self._zap = ZAPv2(proxies=self._proxies, apikey=api_key, validate_status_code=True)
        self._settings = settings
        self._lock = threading.Lock()

    @contextmanager
    def open(self, url: str) -> Iterator[ScanSession]:
        if not self._lock.acquire(blocking=False):
            raise ScanError("Ya hay un escaneo en curso.")
        try:
            yield self._start(url)
        finally:
            self._lock.release()

    def _start(self, url: str) -> ScanSession:
        with translated_errors():
            self._zap.network.set_connection_timeout(self._settings.request_timeout_seconds)
            target = self._resolve_final_url(url)
            parts = urlsplit(target)
            ctx_id = self._prepare(parts.netloc)
            return ScanSession(self._zap, target, f"{parts.scheme}://{parts.netloc}",
                               ctx_name=_CONTEXT_NAME, ctx_id=ctx_id, settings=self._settings)

    def _prepare(self, netloc: str) -> str:
        """Sesión limpia, alcance y política. Devuelve el id del contexto."""
        zap = self._zap

        zap.core.new_session(overwrite="true")  # borra contexto y datos del escaneo anterior
        zap.core.set_mode("protect")  # los ataques solo van a lo que esté en alcance

        ctx_id = zap.context.new_context(_CONTEXT_NAME)
        zap.context.include_in_context(_CONTEXT_NAME, rf"^https?://{re.escape(netloc)}(/.*)?$")
        zap.context.exclude_from_context(_CONTEXT_NAME, _DISCOVERY_EXCLUDE_PATTERN)
        zap.context.set_context_in_scope(_CONTEXT_NAME, "true")

        zap.spider.set_option_max_depth(self._settings.discovery_max_depth)
        zap.spider.set_option_thread_count(_DISCOVERY_WORKERS)
        zap.spider.set_option_max_duration(
            math.ceil(self._settings.discovery_seconds / 60.0)
        )

        forms = "true" if _DISCOVERY_FORMS_ENABLED else "false"
        zap.spider.set_option_post_form(forms)
        zap.spider.set_option_process_form(forms)

        zap.ascan.set_option_max_scan_duration_in_mins(
            math.ceil(self._settings.analysis_seconds / 60.0)
        )

        return str(ctx_id)

    def _resolve_final_url(self, url: str) -> str:
        timeout = (_CONNECT_TIMEOUT, _API_READ_TIMEOUT * 2 + _READ_GRACE)
        current = url
        try:
            for _ in range(_MAX_REDIRECTS + 1):
                current = validate_target(current, allow_private=self._settings.allow_private_targets)
                with requests.get(
                        current,
                        proxies=self._proxies,
                        verify=False,
                        stream=True,
                        allow_redirects=False,
                        timeout=timeout,
                ) as r:
                    if r.status_code in (502, 503, 504):
                        raise TargetError("El objetivo no responde.")
                    if not r.is_redirect:
                        return r.url
                    current = urljoin(r.url, r.headers["Location"])
        except requests.ReadTimeout as exc:
            raise TargetError("El objetivo tardó demasiado en responder.") from exc
        raise TargetError("El objetivo redirige demasiadas veces.")
