from __future__ import annotations

from dataclasses import dataclass

__all__ = ["ReferenceContext"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceContext:
    value: object
