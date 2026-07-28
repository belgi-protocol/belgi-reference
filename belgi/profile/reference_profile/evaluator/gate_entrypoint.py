from __future__ import annotations

from belgi.core import Evaluator, EvidenceState
from belgi.profile.edition import ProfileIdentifier

from .gate import ensure_reference_profile_evaluator_gates

__all__ = ["validate_reference_profile_evaluator_gates"]


def validate_reference_profile_evaluator_gates(
    *,
    profile_identifier: ProfileIdentifier,
    admission_artifact: object,
    evaluator: Evaluator,
    evidence_state: EvidenceState,
) -> None:
    ensure_reference_profile_evaluator_gates(
        profile_identifier=profile_identifier,
        admission_artifact=admission_artifact,
        evaluator=evaluator,
        evidence_state=evidence_state,
    )
