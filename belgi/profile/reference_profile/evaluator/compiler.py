from __future__ import annotations

from belgi.core import Evaluator
from belgi.profile.edition import ProfileIdentifier
from belgi.profile.reference_profile.admission_artifact import (
    reference_profile_require_matching_admission_config,
)
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvaluatorCompileError,
)

from .construction import reference_profile_evaluator_from_admission_config
from .semantics.selection import (
    reference_profile_require_evaluator_semantics,
)

__all__ = [
    "compile_reference_profile_evaluator_artifact",
]


def compile_reference_profile_evaluator_artifact(
    *,
    profile_identifier: ProfileIdentifier,
    admission_artifact: object,
) -> Evaluator:
    admission_artifact = reference_profile_require_matching_admission_config(
        admission_artifact=admission_artifact,
        profile_identifier=profile_identifier,
        error_type=ReferenceProfileEvaluatorCompileError,
        owner_label="reference-profile evaluator",
    )
    evaluator = reference_profile_evaluator_from_admission_config(
        admission_artifact=admission_artifact
    )
    reference_profile_require_evaluator_semantics(evaluator=evaluator)
    return evaluator
