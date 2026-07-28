from __future__ import annotations

from collections.abc import Iterable

from .state import EvidenceState

__all__ = ["project_evidence_state"]


def project_evidence_state(*, items: Iterable[object]) -> EvidenceState:
    return EvidenceState(items=tuple(items))
