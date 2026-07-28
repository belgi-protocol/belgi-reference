from __future__ import annotations

from belgi.core import EvidenceState, JudgedObject
from belgi.profile.edition import ProfileIdentifier

from .gate import ensure_reference_profile_required_evidence_bindings

__all__ = ["validate_reference_profile_required_evidence_bindings"]


def validate_reference_profile_required_evidence_bindings(
    *,
    profile_identifier: ProfileIdentifier,
    admission_artifact: object,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
) -> None:
    ensure_reference_profile_required_evidence_bindings(
        profile_identifier=profile_identifier,
        admission_artifact=admission_artifact,
        judged_object=judged_object,
        evidence_state=evidence_state,
    )
