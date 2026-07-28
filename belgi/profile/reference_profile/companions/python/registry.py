from __future__ import annotations

from belgi.core import SatRegistration, SemanticsKey
from belgi.profile.companions.python.identifiers.conditions import TESTS_PASS
from belgi.profile.edition import ExactEditionBinding
from belgi.profile.governance import ConditionId
from belgi.profile.reference_profile.evaluator.semantics.contracts import (
    ConditionSemanticsBinding,
    ProfileSatFunction,
    SemanticsProviderWitness,
)
from belgi.profile.reference_profile.evidence.semantics import adapt_profile_sat

from .tests import python_tests_pass_sat

__all__ = [
    "python_companion_provider_witness",
    "python_companion_sat_registrations",
    "python_companion_semantics",
]


def _python_companion_binding(
    *,
    condition_id: ConditionId,
    implementation: ProfileSatFunction,
) -> ConditionSemanticsBinding:
    return ConditionSemanticsBinding(
        condition_id=condition_id,
        semantics_key=SemanticsKey(str(condition_id)),
        implementation=implementation,
    )


def python_companion_semantics() -> tuple[ConditionSemanticsBinding, ...]:
    return (
        _python_companion_binding(
            condition_id=TESTS_PASS,
            implementation=python_tests_pass_sat,
        ),
    )


def python_companion_provider_witness(
    *,
    binding: ConditionSemanticsBinding,
    companion_binding: ExactEditionBinding,
) -> SemanticsProviderWitness:
    sat = adapt_profile_sat(binding.implementation)
    entrypoint = getattr(sat, "__belgi_provider_entrypoint__", None)
    if not isinstance(entrypoint, str) or not entrypoint:
        raise TypeError("Python-companion Sat provider entrypoint must be text.")
    return SemanticsProviderWitness(
        semantics_key=binding.semantics_key,
        source_designator=companion_binding.immutable_designator,
        provider_identifier=str(companion_binding.family_identifier),
        callable_entrypoint=entrypoint,
    )


def python_companion_sat_registrations(
    *,
    companion_binding: ExactEditionBinding | None = None,
) -> tuple[SatRegistration, ...]:
    return tuple(
        SatRegistration(
            semantics_key=binding.semantics_key,
            sat=adapt_profile_sat(binding.implementation),
            provider_witnesses=(
                ()
                if companion_binding is None
                else (
                    python_companion_provider_witness(
                        binding=binding,
                        companion_binding=companion_binding,
                    ),
                )
            ),
        )
        for binding in python_companion_semantics()
    )
