from __future__ import annotations

from belgi.core import EvidenceState, JudgedObject
from belgi.profile.edition import ProfileIdentifier
from belgi.profile.reference_profile.admission_artifact import (
    reference_profile_require_matching_admission_config,
)
from belgi.profile.reference_profile.declarations import (
    EvidencePresenceDeclaration,
    declared_profile_condition,
)
from belgi.profile.reference_profile.evidence.semantics import (
    required_evidence_presence_failures,
)
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvidenceStateCompileError,
)
from belgi.profile.reference_profile.identifiers import REQUIRED_EVIDENCE_PRESENT

__all__ = ["ensure_reference_profile_required_evidence_bindings"]


def ensure_reference_profile_required_evidence_bindings(
    *,
    profile_identifier: ProfileIdentifier,
    admission_artifact: object,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
) -> None:
    typed_admission_artifact = reference_profile_require_matching_admission_config(
        admission_artifact=admission_artifact,
        profile_identifier=profile_identifier,
        error_type=ReferenceProfileEvidenceStateCompileError,
        owner_label="evidence validation",
    )
    declaration = typed_admission_artifact.declaration_for(
        condition_id=str(REQUIRED_EVIDENCE_PRESENT)
    )
    if not isinstance(declaration, EvidencePresenceDeclaration):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="required_evidence_present",
            detail=(
                "AdmissionConfig.required-evidence-present declaration must be "
                "an EvidencePresenceDeclaration."
            ),
        )
    failures = required_evidence_presence_failures(
        judged_object=judged_object,
        evidence_state=evidence_state,
        condition=declared_profile_condition(declaration=declaration),
    )
    if failures:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="required_evidence_present",
            detail="; ".join(failures),
        )
