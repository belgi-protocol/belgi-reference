from __future__ import annotations

from datetime import date, datetime, timezone
from time import monotonic_ns as _monotonic_ns
from typing import TypeAlias

UtcDate: TypeAlias = date


def utc_now_rfc3339() -> str:
    return datetime.now(timezone.utc).isoformat()


def monotonic_time_ns() -> int:
    return _monotonic_ns()


__all__ = [
    "UtcDate",
    "monotonic_time_ns",
    "utc_now_rfc3339",
]
