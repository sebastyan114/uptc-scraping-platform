import hashlib
from urllib.parse import parse_qsl, urlsplit


def _normalize(matched_at: str) -> str:
    if "://" not in matched_at:
        return matched_at.lower()
    p = urlsplit(matched_at)
    params = ",".join(sorted(k for k, _ in parse_qsl(p.query, keep_blank_values=True)))
    return f"{p.scheme.lower()}://{p.netloc.lower()}{p.path}?{params}"


def compute_fingerprint(rule_id: str, matched_at: str, matcher_name: str | None) -> str:
    raw = "|".join((rule_id, _normalize(matched_at), matcher_name or ""))
    return hashlib.sha256(raw.encode()).hexdigest()