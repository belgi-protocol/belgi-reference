from __future__ import annotations

from belgi.core import (
    Condition,
    Evaluator,
    ResolvedConditionSemantics,
    SatRegistry,
    UndesignatedConditionSemantics,
    UnrecoverableConditionSemantics,
)
from belgi.profile.governance import ConditionId as GovernanceConditionId
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvaluatorCompileError,
)

from .admissibility import build_reference_profile_evaluator_sat_registry
from .registry import reference_profile_condition_semantics_binding

__all__ = ["reference_profile_require_evaluator_semantics"]


def reference_profile_require_evaluator_semantics(
    *,
    evaluator: Evaluator,
) -> SatRegistry:
    sat_registry = build_reference_profile_evaluator_sat_registry()
    for condition in evaluator.declared_conditions:
        _require_selected_condition_semantics(
            condition=condition,
            sat_registry=sat_registry,
        )
    return sat_registry


def _require_selected_condition_semantics(
    *,
    condition: Condition,
    sat_registry: SatRegistry,
) -> None:
    determining_semantics = condition.determining_semantics
    condition_identifier = GovernanceConditionId(str(condition.condition_id))
    if isinstance(determining_semantics, UndesignatedConditionSemantics):
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="semantics_binding",
            detail=(
                "selected condition has no declared semantics binding: "
                f"{condition_identifier!s}."
            ),
        )
    if isinstance(determining_semantics, UnrecoverableConditionSemantics):
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="semantics_binding",
            detail=(
                "selected condition resolves to unrecoverable semantics: "
                f"{condition_identifier!s}."
            ),
        )
    if not isinstance(determining_semantics, ResolvedConditionSemantics):
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="semantics_binding",
            detail=(
                "selected condition has unsupported evaluator semantics state: "
                f"{condition_identifier!s}."
            ),
        )
    binding = reference_profile_condition_semantics_binding(
        condition_id=condition_identifier
    )
    if binding is None:
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="semantics_binding",
            detail=(
                "selected condition is not registered in the reference-profile "
                f"semantics registry: {condition_identifier!s}."
            ),
        )
    if determining_semantics.semantics_key != binding.semantics_key:
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="semantics_binding",
            detail=(
                "selected condition semantics key does not match the "
                "reference-profile registry binding: "
                f"{condition_identifier!s}."
            ),
        )
    if sat_registry.resolve(semantics_key=determining_semantics.semantics_key) is None:
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="semantics_binding",
            detail=(
                "reference-profile SAT registry has no callable for selected "
                f"condition {condition_identifier!s}."
            ),
        )
