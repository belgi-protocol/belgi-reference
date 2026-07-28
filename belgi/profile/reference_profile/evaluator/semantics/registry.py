from __future__ import annotations

from belgi.core import SatRegistration, SatRegistry, SemanticsKey
from belgi.profile.companions.agent_admission.edition import (
    COMPANION_IDENTIFIER as AGENT_ADMISSION_COMPANION_IDENTIFIER,
)
from belgi.profile.companions.python.edition import (
    COMPANION_IDENTIFIER as PYTHON_COMPANION_IDENTIFIER,
)
from belgi.profile.edition import ExactEditionBinding
from belgi.profile.governance import ConditionId
from belgi.profile.reference_profile.companions.agent_admission.semantics import (
    agent_admission_companion_sat_registrations,
    agent_admission_companion_semantics,
)
from belgi.profile.reference_profile.companions.python.registry import (
    python_companion_sat_registrations,
    python_companion_semantics,
)
from belgi.profile.reference_profile.config.exact_editions import (
    resolve_reference_profile_companion_binding,
    supported_reference_profile_edition_bindings,
)
from belgi.profile.reference_profile.evidence.semantics import (
    adapt_profile_sat,
    required_evidence_present_sat,
)
from belgi.profile.reference_profile.finite_evaluator.registrations import (
    finite_evaluator_sat_registrations,
)
from belgi.profile.reference_profile.identifiers.conditions import (
    ANALYSIS_POLICY_SATISFIED,
    BUILD_POLICY_SATISFIED,
    CHANGE_BASIS_RESOLVED,
    COVERAGE_POLICY_SATISFIED,
    DEPENDENCY_POLICY_SATISFIED,
    ENVIRONMENT_COMPATIBILITY_SATISFIED,
    REQUIRED_EVIDENCE_PRESENT,
    REVIEW_POLICY_SATISFIED,
    TEST_POLICY_SATISFIED,
)
from belgi.profile.reference_profile.identifiers.profile import PROFILE_IDENTIFIER

from .analysis import analysis_policy_sat
from .build import build_policy_sat
from .change_basis import change_basis_sat
from .contracts import (
    ConditionSemanticsBinding,
    ProfileSatFunction,
    SemanticsProviderWitness,
)
from .coverage import coverage_policy_sat
from .dependency import dependency_policy_sat
from .environment import environment_compatibility_sat
from .review import review_policy_sat
from .tests import test_policy_sat

__all__ = [
    "reference_profile_condition_semantics_binding",
    "reference_profile_sat_registrations",
    "reference_profile_semantics",
    "register_reference_profile_semantics",
]


def _reference_profile_binding(
    *,
    condition_id: ConditionId,
    implementation: ProfileSatFunction,
) -> ConditionSemanticsBinding:
    return ConditionSemanticsBinding(
        condition_id=condition_id,
        semantics_key=SemanticsKey(str(condition_id)),
        implementation=implementation,
    )


def reference_profile_semantics() -> tuple[ConditionSemanticsBinding, ...]:
    return (
        _reference_profile_binding(
            condition_id=CHANGE_BASIS_RESOLVED,
            implementation=change_basis_sat,
        ),
        _reference_profile_binding(
            condition_id=REQUIRED_EVIDENCE_PRESENT,
            implementation=required_evidence_present_sat,
        ),
        _reference_profile_binding(
            condition_id=BUILD_POLICY_SATISFIED,
            implementation=build_policy_sat,
        ),
        _reference_profile_binding(
            condition_id=TEST_POLICY_SATISFIED,
            implementation=test_policy_sat,
        ),
        _reference_profile_binding(
            condition_id=COVERAGE_POLICY_SATISFIED,
            implementation=coverage_policy_sat,
        ),
        _reference_profile_binding(
            condition_id=REVIEW_POLICY_SATISFIED,
            implementation=review_policy_sat,
        ),
        _reference_profile_binding(
            condition_id=DEPENDENCY_POLICY_SATISFIED,
            implementation=dependency_policy_sat,
        ),
        _reference_profile_binding(
            condition_id=ANALYSIS_POLICY_SATISFIED,
            implementation=analysis_policy_sat,
        ),
        _reference_profile_binding(
            condition_id=ENVIRONMENT_COMPATIBILITY_SATISFIED,
            implementation=environment_compatibility_sat,
        ),
    )


def reference_profile_condition_semantics_binding(
    *,
    condition_id: ConditionId,
) -> ConditionSemanticsBinding | None:
    matches = tuple(
        binding
        for binding in (
            reference_profile_semantics()
            + agent_admission_companion_semantics()
            + python_companion_semantics()
        )
        if binding.condition_id == condition_id
    )
    if len(matches) > 1:
        raise ValueError(
            "reference-profile semantics registry contains duplicate "
            f"bindings for {condition_id!s}."
        )
    if not matches:
        return None
    return matches[0]


def _reference_profile_provider_witnesses_for_binding(
    *,
    binding: ConditionSemanticsBinding,
    profile_edition_binding: ExactEditionBinding,
) -> tuple[SemanticsProviderWitness, ...]:
    return (
        SemanticsProviderWitness(
            semantics_key=binding.semantics_key,
            source_designator=profile_edition_binding.immutable_designator,
            provider_identifier="belgi.reference-profile.local-semantics",
            callable_entrypoint=_reference_profile_provider_entrypoint(
                binding.implementation
            ),
        ),
    )


def _reference_profile_provider_entrypoint(
    implementation: ProfileSatFunction,
) -> str:
    module = getattr(implementation, "__module__", "")
    qualname = getattr(implementation, "__qualname__", "")
    if not module or not qualname:
        raise TypeError("profile Sat implementation must expose a stable entrypoint.")
    return f"{module}:{qualname}"


def _reference_profile_semantics_edition_binding(
    *,
    edition_bindings: tuple[ExactEditionBinding, ...],
    family_identifier: str,
) -> ExactEditionBinding:
    matches = tuple(
        binding
        for binding in edition_bindings
        if str(binding.family_identifier) == family_identifier
    )
    if len(matches) != 1:
        raise ValueError(
            "reference-profile semantics require exactly one exact-edition "
            f"binding for {family_identifier!r}."
        )
    return matches[0]


def reference_profile_sat_registrations(
    *,
    edition_bindings: tuple[ExactEditionBinding, ...] | None = None,
) -> tuple[SatRegistration, ...]:
    """Produce core Sat registrations for the reference profile surface."""

    selected_bindings = (
        (
            *supported_reference_profile_edition_bindings(),
            resolve_reference_profile_companion_binding(
                companion_identifier=str(AGENT_ADMISSION_COMPANION_IDENTIFIER),
            ),
            resolve_reference_profile_companion_binding(
                companion_identifier=str(PYTHON_COMPANION_IDENTIFIER),
            ),
        )
        if edition_bindings is None
        else edition_bindings
    )
    profile_edition_binding = _reference_profile_semantics_edition_binding(
        edition_bindings=selected_bindings,
        family_identifier=str(PROFILE_IDENTIFIER),
    )
    agent_admission_companion_binding = _reference_profile_semantics_edition_binding(
        edition_bindings=selected_bindings,
        family_identifier=str(AGENT_ADMISSION_COMPANION_IDENTIFIER),
    )
    python_companion_binding = _reference_profile_semantics_edition_binding(
        edition_bindings=selected_bindings,
        family_identifier=str(PYTHON_COMPANION_IDENTIFIER),
    )

    reference_registrations = tuple(
        SatRegistration(
            semantics_key=binding.semantics_key,
            sat=adapt_profile_sat(binding.implementation),
            provider_witnesses=_reference_profile_provider_witnesses_for_binding(
                binding=binding,
                profile_edition_binding=profile_edition_binding,
            ),
        )
        for binding in reference_profile_semantics()
    )
    return (
        *reference_registrations,
        *finite_evaluator_sat_registrations(
            profile_binding=profile_edition_binding,
        ),
        *agent_admission_companion_sat_registrations(
            companion_binding=agent_admission_companion_binding,
        ),
        *python_companion_sat_registrations(
            companion_binding=python_companion_binding,
        ),
    )


def register_reference_profile_semantics(
    *,
    registry: SatRegistry,
    edition_bindings: tuple[ExactEditionBinding, ...] | None = None,
    replace: bool = False,
) -> SatRegistry:
    return registry.with_registrations(
        registrations=reference_profile_sat_registrations(
            edition_bindings=edition_bindings,
        ),
        replace=replace,
    )
