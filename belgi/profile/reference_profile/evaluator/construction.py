from __future__ import annotations

from belgi.core import (
    ConditionId,
    ConditionSemantics,
    Evaluator,
    ResolvedConditionSemantics,
    UndesignatedConditionSemantics,
    UnrecoverableConditionSemantics,
)
from belgi.profile.reference_profile.config.model import AdmissionConfig
from belgi.profile.reference_profile.declarations import (
    ProfileCondition,
    ProfileConditionDeclaration,
)
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvaluatorCompileError,
)
from belgi.profile.reference_profile.identifiers.conditions import (
    FOUNDATION_CONDITIONS,
)

from .carrier.projection import reference_profile_aligned_evaluator_carrier
from .semantics.registry import reference_profile_condition_semantics_binding

__all__ = ["reference_profile_evaluator_from_admission_config"]


def reference_profile_evaluator_from_admission_config(
    *,
    admission_artifact: AdmissionConfig,
) -> Evaluator:
    declarations = tuple(admission_artifact.condition_declarations)
    _require_foundation_conditions(declarations=declarations)
    _require_additional_go_condition(declarations=declarations)
    admission_artifact.validate_evaluator_carrier(
        evaluator_carrier=reference_profile_aligned_evaluator_carrier(
            admission_artifact=admission_artifact
        )
    )
    try:
        return Evaluator(
            declared_conditions=tuple(
                _compiled_condition_from_declaration(declaration=declaration)
                for declaration in declarations
            ),
        )
    except ValueError as exc:
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="declared_conditions",
            detail=(
                "evaluator construction could not normalize the declared condition set."
            ),
        ) from exc


def _require_foundation_conditions(
    *,
    declarations: tuple[ProfileConditionDeclaration, ...],
) -> None:
    declared_condition_ids = frozenset(
        str(declaration.condition_id) for declaration in declarations
    )
    missing = [
        str(condition_id)
        for condition_id in FOUNDATION_CONDITIONS
        if str(condition_id) not in declared_condition_ids
    ]
    if missing:
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="declared_conditions",
            detail=(
                "evaluator construction requires the foundation "
                "conditions: " + ", ".join(sorted(missing))
            ),
        )


def _require_additional_go_condition(
    *,
    declarations: tuple[ProfileConditionDeclaration, ...],
) -> None:
    foundation_condition_ids = frozenset(
        str(condition_id) for condition_id in FOUNDATION_CONDITIONS
    )
    additional_condition_ids = {
        str(declaration.condition_id)
        for declaration in declarations
        if str(declaration.condition_id) not in foundation_condition_ids
    }
    if not additional_condition_ids:
        raise ReferenceProfileEvaluatorCompileError(
            semantic_slice="declared_conditions",
            detail=(
                "evaluator construction requires at least one "
                "additional go condition beyond the foundation pair."
            ),
        )


def _compiled_condition_from_declaration(
    *,
    declaration: ProfileConditionDeclaration,
) -> ProfileCondition:
    return ProfileCondition(
        condition_id=ConditionId(str(declaration.condition_id)),
        determining_semantics=_compiled_condition_semantics(declaration=declaration),
        profile_declaration=declaration,
    )


def _compiled_condition_semantics(
    *,
    declaration: ProfileConditionDeclaration,
) -> ConditionSemantics:
    try:
        binding = reference_profile_condition_semantics_binding(
            condition_id=declaration.condition_id
        )
    except ValueError:
        return UnrecoverableConditionSemantics()
    if binding is None:
        return UndesignatedConditionSemantics()
    return ResolvedConditionSemantics(semantics_key=binding.semantics_key)
