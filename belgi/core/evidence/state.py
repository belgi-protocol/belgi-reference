from __future__ import annotations

from dataclasses import dataclass

__all__ = ["EvidenceState"]


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceState:
    items: tuple[object, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "items", tuple(self.items))
