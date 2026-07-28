from __future__ import annotations

from belgi.core import Evaluator
from belgi.profile.edition import ProfileIdentifier

from .compiler import compile_reference_profile_evaluator_artifact

__all__ = [
    "compile_reference_profile_evaluator_document",
]


def compile_reference_profile_evaluator_document(
    *,
    profile_identifier: ProfileIdentifier,
    admission_artifact: object,
) -> Evaluator:
    """Compile profile-owned evaluator meaning from the declared admission artifact."""
    return compile_reference_profile_evaluator_artifact(
        profile_identifier=profile_identifier,
        admission_artifact=admission_artifact,
    )
