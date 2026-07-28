from __future__ import annotations

from typing import TypeAlias as _TypeAlias

from .item import EvidenceItem, EvidenceItemId, EvidenceKindId
from .projection import project_evidence_state
from .state import EvidenceState

E: _TypeAlias = EvidenceState

__all__ = [
    "E",
    "EvidenceItem",
    "EvidenceItemId",
    "EvidenceKindId",
    "EvidenceState",
    "project_evidence_state",
]
