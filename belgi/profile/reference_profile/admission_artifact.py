from __future__ import annotations

from typing import TypeAlias

from belgi.profile.edition import ProfileIdentifier

from .config.model import AdmissionConfig
from .exceptions import (
    ReferenceProfileAdmissionCompileError,
    ReferenceProfileEvaluatorCompileError,
    ReferenceProfileEvidenceStateCompileError,
    ReferenceProfileJudgedObjectCompileError,
)

__all__ = ["reference_profile_require_matching_admission_config"]

_ReferenceProfileAdmissionArtifactErrorType: TypeAlias = (
    type[ReferenceProfileAdmissionCompileError]
    | type[ReferenceProfileEvaluatorCompileError]
    | type[ReferenceProfileEvidenceStateCompileError]
    | type[ReferenceProfileJudgedObjectCompileError]
)


def reference_profile_require_matching_admission_config(
    *,
    admission_artifact: object,
    profile_identifier: ProfileIdentifier,
    error_type: _ReferenceProfileAdmissionArtifactErrorType,
    owner_label: str,
) -> AdmissionConfig:
    if not isinstance(admission_artifact, AdmissionConfig):
        raise error_type(
            semantic_slice="admission_artifact",
            detail=(
                f"{owner_label} lowering requires a matching AdmissionConfig artifact."
            ),
        )
    if str(admission_artifact.profile_edition.family_identifier) != str(
        profile_identifier
    ):
        raise error_type(
            semantic_slice="admission_artifact",
            detail=(
                "admission artifact profile exact-edition does not match the "
                "product-selected profile identifier."
            ),
        )
    return admission_artifact
