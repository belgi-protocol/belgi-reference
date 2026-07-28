from __future__ import annotations

from belgi.profile.governance import EvaluatorParameterId

__all__ = [
    "ALL_PARAMETER_IDS",
    "AUTHORITY_LEVEL_PARAMETER",
    "BOUNDARY_PARTICIPATION_PARAMETER",
    "EVIDENCE_SOURCE_CLASS_PARAMETER",
]


EVIDENCE_SOURCE_CLASS_PARAMETER = EvaluatorParameterId(
    "belgi.software-change.parameter.evidence-source-class"
)
BOUNDARY_PARTICIPATION_PARAMETER = EvaluatorParameterId(
    "belgi.software-change.parameter.boundary-participation"
)
AUTHORITY_LEVEL_PARAMETER = EvaluatorParameterId(
    "belgi.software-change.parameter.authority-level"
)

ALL_PARAMETER_IDS: tuple[EvaluatorParameterId, ...] = (
    EVIDENCE_SOURCE_CLASS_PARAMETER,
    BOUNDARY_PARTICIPATION_PARAMETER,
    AUTHORITY_LEVEL_PARAMETER,
)
