from __future__ import annotations

from dataclasses import dataclass

from belgi.core.evaluator.exceptions import ProjectionError

from .admission_subject import AdmissionSubject
from .reference_context import ReferenceContext

__all__ = ["JudgedObject", "project_judged_object"]


@dataclass(frozen=True, slots=True, kw_only=True)
class JudgedObject:
    admission_subject: AdmissionSubject
    reference_context: ReferenceContext

    def __post_init__(self) -> None:
        if not isinstance(self.admission_subject, AdmissionSubject):
            raise ProjectionError(
                "JudgedObject admission_subject must be an AdmissionSubject."
            )
        if not isinstance(self.reference_context, ReferenceContext):
            raise ProjectionError(
                "JudgedObject reference_context must be a ReferenceContext."
            )


def project_judged_object(
    *,
    admission_subject: AdmissionSubject,
    reference_context: ReferenceContext,
) -> JudgedObject:
    return JudgedObject(
        admission_subject=admission_subject,
        reference_context=reference_context,
    )
