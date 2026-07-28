from __future__ import annotations

from typing import TypeAlias as _TypeAlias

from .engine import active_conditions, apply_evaluator
from .exceptions import (
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
from .model import (
    Condition,
    ConditionId,
    ConditionSemantics,
    Evaluator,
    ResolvedConditionSemantics,
    SemanticsKey,
    UndesignatedConditionSemantics,
    UnrecoverableConditionSemantics,
)
from .sat import Sat, SatRegistration, SatRegistry
from .verdict import GO, NO_GO, Verdict

F: _TypeAlias = Evaluator
V: _TypeAlias = Verdict

__all__ = [
    "GO",
    "NO_GO",
    "Condition",
    "ConditionId",
    "ConditionSemantics",
    "CoreError",
    "DuplicateIdentifierError",
    "DuplicateSatRegistrationError",
    "Evaluator",
    "EvaluatorError",
    "EvaluatorModelError",
    "F",
    "ProjectionError",
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
]
