from __future__ import annotations

from collections.abc import Mapping

from belgi.core import EvidenceState, project_evidence_state
from belgi.profile.edition import ProfileIdentifier
from belgi.profile.reference_profile.admission_artifact import (
    reference_profile_require_matching_admission_config,
)
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvidenceStateCompileError,
)

from .lowering import reference_profile_evidence_items_from_transport
from .transport import reference_profile_evidence_transport_from_document

__all__ = [
    "compile_reference_profile_evidence_state_transport_document",
]


def compile_reference_profile_evidence_state_transport_document(
    *,
    profile_identifier: ProfileIdentifier,
    admission_artifact: object,
    document: Mapping[str, object],
) -> EvidenceState:
    typed_admission_artifact = reference_profile_require_matching_admission_config(
        admission_artifact=admission_artifact,
        profile_identifier=profile_identifier,
        error_type=ReferenceProfileEvidenceStateCompileError,
        owner_label="evidence-state",
    )
    transport = reference_profile_evidence_transport_from_document(document=document)
    return project_evidence_state(
        items=reference_profile_evidence_items_from_transport(
            admission_artifact=typed_admission_artifact,
            transport=transport,
        )
    )
