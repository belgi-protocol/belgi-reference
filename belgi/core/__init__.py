from __future__ import annotations

from typing import TypeAlias as _TypeAlias

from .evaluator.engine import active_conditions, apply_evaluator
from .evaluator.exceptions import (
    CoreError,
    DuplicateIdentifierError,
    DuplicateSatRegistrationError,
    EvaluatorError,
    EvaluatorModelError,
    ProjectionError,
    SatExecutionError,
    SatRegistryError,
    SemanticConstructionError,
)
from .evaluator.model import (
    Condition,
    ConditionId,
    ConditionSemantics,
    Evaluator,
    ResolvedConditionSemantics,
    SemanticsKey,
    UndesignatedConditionSemantics,
    UnrecoverableConditionSemantics,
)
from .evaluator.sat.protocol import Sat
from .evaluator.sat.registry import SatRegistration, SatRegistry
from .evaluator.verdict import GO, NO_GO, Verdict
from .evidence.item import EvidenceItem, EvidenceItemId, EvidenceKindId
from .evidence.projection import project_evidence_state
from .evidence.state import EvidenceState
from .judged.admission_subject import AdmissionSubject
from .judged.projection import JudgedObject, project_judged_object
from .judged.reference_context import ReferenceContext

F: _TypeAlias = Evaluator
V: _TypeAlias = Verdict
E: _TypeAlias = EvidenceState
J: _TypeAlias = JudgedObject

__all__ = [
    "GO",
    "NO_GO",
    "AdmissionSubject",
    "Condition",
    "ConditionId",
    "ConditionSemantics",
    "CoreError",
    "DuplicateIdentifierError",
    "DuplicateSatRegistrationError",
    "E",
    "Evaluator",
    "EvaluatorError",
    "EvaluatorModelError",
    "EvidenceItem",
    "EvidenceItemId",
    "EvidenceKindId",
    "EvidenceState",
    "F",
    "J",
    "JudgedObject",
    "ProjectionError",
    "ReferenceContext",
    "ResolvedConditionSemantics",
    "Sat",
    "SatExecutionError",
    "SatRegistration",
    "SatRegistry",
    "SatRegistryError",
    "SemanticConstructionError",
    "SemanticsKey",
    "UndesignatedConditionSemantics",
    "UnrecoverableConditionSemantics",
    "V",
    "Verdict",
    "active_conditions",
    "apply_evaluator",
    "project_evidence_state",
    "project_judged_object",
]
