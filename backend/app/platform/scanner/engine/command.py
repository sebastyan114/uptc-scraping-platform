from collections.abc import Sequence


def build_command(
    *,
    binary: str = "nuclei",
    targets: Sequence[str],
    request_timeout_seconds: int,
    max_scan_seconds: int,
) -> list[str]:
    return [
        binary,
        *(f"-target {target}" for target in targets), # cada objetivo como argumento separado

        # Formato de salida (compatible con el parser)
        "-jsonl=true",                              # un JSON por línea: permite leer en streaming
        "-omit-raw=false",                          # incluir request/response en cada hallazgo
        "-omit-template=true",                      # no incluir el YAML del template (pesa mucho)
        "-silent=true",                             # stdout solo con resultados, sin banner ni logs
        "-no-color=true",                           # sin códigos ANSI que corrompan el JSON

        # Límites de tiempo
        "-timeout", str(request_timeout_seconds),   # por petición, en segundos
        "-max-time", f"{max_scan_seconds}s",        # total del escaneo, como duración
    ]