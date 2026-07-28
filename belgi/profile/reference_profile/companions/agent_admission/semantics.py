from __future__ import annotations

from typing import TYPE_CHECKING, cast

from belgi.core import SatRegistration, SemanticsKey
from belgi.profile.companions.agent_admission.identifiers import (
    AGENT_DECISION_ACCEPTED,
    AGENT_TOOL_USE_RECORDED,
)
from belgi.profile.edition import ExactEditionBinding
from belgi.profile.exceptions import ProfileError
from belgi.profile.governance import ConditionId
from belgi.profile.reference_profile.declarations import (
    EvidencePresenceDeclaration,
    OutcomePolicyDeclaration,
)
from belgi.profile.reference_profile.evaluator.semantics.build import (
    evaluate_outcome_policy,
)
from belgi.profile.reference_profile.evaluator.semantics.contracts import (
    ConditionSemanticsBinding,
    ProfileSatFunction,
    SemanticsProviderWitness,
)
from belgi.profile.reference_profile.evidence.semantics import (
    adapt_profile_sat,
    satisfies_required_evidence_present,
    unwrap_profile_declaration,
)

if TYPE_CHECKING:
    from belgi.core import EvidenceState, JudgedObject

__all__ = [
    "agent_admission_companion_provider_witness",
    "agent_admission_companion_sat_registrations",
    "agent_admission_companion_semantics",
    "agent_decision_accepted_sat",
    "agent_tool_use_recorded_sat",
    "satisfies_agent_decision_accepted",
    "satisfies_agent_tool_use_recorded",
]


def satisfies_agent_decision_accepted(
    *,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
    condition: object,
) -> bool:
    del judged_object
    declaration = unwrap_profile_declaration(
        condition,
        OutcomePolicyDeclaration,
    )
    return evaluate_outcome_policy(
        evidence_state=evidence_state,
        declaration=declaration,
    )


def agent_decision_accepted_sat(
    judged_object: object,
    evidence_state: object,
    condition: object,
) -> bool:
    try:
        return satisfies_agent_decision_accepted(
            judged_object=cast("JudgedObject", judged_object),
            evidence_state=cast("EvidenceState", evidence_state),
            condition=condition,
        )
    except (AttributeError, ProfileError, TypeError, ValueError):
        return False


def satisfies_agent_tool_use_recorded(
    *,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
    condition: object,
) -> bool:
    declaration = unwrap_profile_declaration(
        condition,
        EvidencePresenceDeclaration,
    )
    return satisfies_required_evidence_present(
        judged_object=judged_object,
        evidence_state=evidence_state,
        condition=declaration,
    )


def agent_tool_use_recorded_sat(
    judged_object: object,
    evidence_state: object,
    condition: object,
) -> bool:
    try:
        return satisfies_agent_tool_use_recorded(
            judged_object=cast("JudgedObject", judged_object),
            evidence_state=cast("EvidenceState", evidence_state),
            condition=condition,
        )
    except (AttributeError, ProfileError, TypeError, ValueError):
        return False


def _agent_admission_companion_binding(
    *,
    condition_id: ConditionId,
    implementation: ProfileSatFunction,
) -> ConditionSemanticsBinding:
    return ConditionSemanticsBinding(
        condition_id=condition_id,
        semantics_key=SemanticsKey(str(condition_id)),
        implementation=implementation,
    )


def agent_admission_companion_semantics() -> tuple[ConditionSemanticsBinding, ...]:
    return (
        _agent_admission_companion_binding(
            condition_id=AGENT_DECISION_ACCEPTED,
            implementation=agent_decision_accepted_sat,
        ),
        _agent_admission_companion_binding(
            condition_id=AGENT_TOOL_USE_RECORDED,
            implementation=agent_tool_use_recorded_sat,
        ),
    )


def agent_admission_companion_provider_witness(
    *,
    binding: ConditionSemanticsBinding,
    companion_binding: ExactEditionBinding,
) -> SemanticsProviderWitness:
    sat = adapt_profile_sat(binding.implementation)
    entrypoint = getattr(sat, "__belgi_provider_entrypoint__", None)
    if not isinstance(entrypoint, str) or not entrypoint:
        raise TypeError("agent-admission Sat provider entrypoint must be text.")
    return SemanticsProviderWitness(
        semantics_key=binding.semantics_key,
        source_designator=companion_binding.immutable_designator,
        provider_identifier=str(companion_binding.family_identifier),
        callable_entrypoint=entrypoint,
    )


def agent_admission_companion_sat_registrations(
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
                    agent_admission_companion_provider_witness(
                        binding=binding,
                        companion_binding=companion_binding,
                    ),
                )
            ),
        )
        for binding in agent_admission_companion_semantics()
    )
