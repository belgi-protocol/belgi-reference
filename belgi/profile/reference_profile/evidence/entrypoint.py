from __future__ import annotations

from collections.abc import Mapping

from belgi.core import EvidenceState
from belgi.profile.edition import ProfileIdentifier

from .compiler import compile_reference_profile_evidence_state_transport_document

__all__ = [
    "compile_reference_profile_evidence_state_document",
]


def compile_reference_profile_evidence_state_document(
    *,
    profile_identifier: ProfileIdentifier,
    admission_artifact: object,
    transport_document: Mapping[str, object],
) -> EvidenceState:
    """Compile profile-owned evidence-state meaning from product observations."""
    return compile_reference_profile_evidence_state_transport_document(
        profile_identifier=profile_identifier,
        admission_artifact=admission_artifact,
        document=transport_document,
    )
