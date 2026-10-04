def build_command(*, binary: str = "nuclei", target: str) -> list[str]:
    return [
        binary,
        "-u", target,
        "-jsonl",  # el parser depende de este formato
        "-silent",  # stdout solo con resultados
        "-nc",  # sin colores ANSI
    ]
