from __future__ import annotations

from dataclasses import dataclass

from .enums import TaskStatus


@dataclass(frozen=True, slots=True, kw_only=True)
class Snapshot[T]:
    data: T
    status: TaskStatus