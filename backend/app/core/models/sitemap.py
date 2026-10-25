from __future__ import annotations

from dataclasses import dataclass

from app.core.models.finding import Risk


@dataclass(frozen=True, slots=True, kw_only=True)
class SiteNode:
    segment: str
    url: str
    children: tuple[SiteNode, ...] = ()
    finding_count: int = 0
    max_risk: Risk | None = None