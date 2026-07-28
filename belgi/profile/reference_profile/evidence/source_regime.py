from __future__ import annotations

from belgi.profile.reference_profile.config.model import AdmissionConfig
from belgi.profile.reference_profile.declarations import SourceBoundaryAssignment
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvidenceStateCompileError,
)

__all__ = [
    "reference_profile_evidence_source_assignment",
]


def reference_profile_evidence_source_assignment(
    *,
    admission_artifact: AdmissionConfig,
    source_class: str,
    label: str,
) -> SourceBoundaryAssignment:
    for assignment in admission_artifact.source_boundary_assignments:
        if str(assignment.source_class) == source_class:
            return assignment
    raise ReferenceProfileEvidenceStateCompileError(
        semantic_slice="source_regime",
        detail=(
            f"{label}.source_class {source_class!r} has no source-boundary "
            "assignment in the declared AdmissionConfig artifact."
        ),
    )
