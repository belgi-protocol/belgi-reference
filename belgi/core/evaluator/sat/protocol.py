from __future__ import annotations

from typing import Protocol

from belgi.core.evaluator.model import Condition
from belgi.core.evidence.state import EvidenceState

__all__ = ["Sat"]


class Sat(Protocol):
    def __call__(
        self,
        *,
        judged: object,
        evidence: EvidenceState,
        condition: Condition,
    ) -> bool: ...
