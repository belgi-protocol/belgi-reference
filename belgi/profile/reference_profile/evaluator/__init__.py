from __future__ import annotations

from belgi.profile.reference_profile.declarations import ProfileCondition
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvaluatorCompileError,
)
from belgi.profile.reference_profile.identifiers.profile import (
    normalize_reference_profile_identifier,
)

from .carrier.parameters import (
    DECLARATION_PARAMETER,
    reference_profile_parameter_value,
)
from .carrier.payload import reference_profile_declaration_from_payload
from .carrier.projection import (
    ReferenceProfileCarrierAlignedEvaluator,
    reference_profile_aligned_evaluator_carrier,
)
from .entrypoint import compile_reference_profile_evaluator_document
from .gate_entrypoint import validate_reference_profile_evaluator_gates
from .semantics import reference_profile_condition_semantics_binding
from .semantics.admissibility import build_reference_profile_evaluator_sat_registry

__all__ = [
    "DECLARATION_PARAMETER",
    "ProfileCondition",
    "ReferenceProfileCarrierAlignedEvaluator",
    "ReferenceProfileEvaluatorCompileError",
    "build_reference_profile_evaluator_sat_registry",
    "compile_reference_profile_evaluator_document",
    "normalize_reference_profile_identifier",
    "reference_profile_aligned_evaluator_carrier",
    "reference_profile_condition_semantics_binding",
    "reference_profile_declaration_from_payload",
    "reference_profile_parameter_value",
    "validate_reference_profile_evaluator_gates",
]
