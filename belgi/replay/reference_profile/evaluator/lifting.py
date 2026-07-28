from __future__ import annotations

import belgi.profile.reference_profile.finite_evaluator as finite_evaluator
from belgi.carrier import DeclaredCondition, EvaluatorCarrier
from belgi.core import (
    ConditionId as CoreConditionId,
)
from belgi.core import (
    ConditionSemantics,
    Evaluator,
    ResolvedConditionSemantics,
    SemanticsKey,
    UndesignatedConditionSemantics,
    UnrecoverableConditionSemantics,
)
from belgi.profile.governance import ConditionId as ProfileConditionId
from belgi.profile.reference_profile.evaluator import (
    DECLARATION_PARAMETER,
    ProfileCondition,
    reference_profile_condition_semantics_binding,
    reference_profile_declaration_from_payload,
    reference_profile_parameter_value,
)
from belgi.replay.lifting.model import ResolvedReferencedSource

__all__ = [
    "reference_profile_evaluator_from_carrier",
    "reference_profile_evaluator_from_resolved_selection",
]


def reference_profile_evaluator_from_carrier(
    *,
    evaluator_carrier: EvaluatorCarrier,
    referenced_sources: tuple[ResolvedReferencedSource, ...],
    provider_witnesses: tuple[object, ...],
    finite_selection_authorized: bool,
) -> Evaluator:
    return reference_profile_evaluator_from_resolved_selection(
        evaluator_carrier=evaluator_carrier,
        resolved_source_designators=_resolved_source_designators(
            referenced_sources=referenced_sources,
        ),
        provider_witness_keys=_provider_witness_keys(
            provider_witnesses=provider_witnesses
        ),
        finite_selection_authorized=finite_selection_authorized,
    )


def reference_profile_evaluator_from_resolved_selection(
    *,
    evaluator_carrier: EvaluatorCarrier,
    resolved_source_designators: frozenset[tuple[str, str, str]],
    provider_witness_keys: frozenset[tuple[tuple[str, str, str], str]],
    finite_selection_authorized: bool,
) -> Evaluator:
    """Induce F from one parsed carrier and already verified source selection."""

    if finite_selection_authorized:
        try:
            return finite_evaluator.induce_finite_evaluator_document(
                document=evaluator_carrier.to_json_object(),
                resolved_source_designators=resolved_source_designators,
                available_semantics_keys=frozenset(
                    SemanticsKey(semantics_key)
                    for source_designator, semantics_key in provider_witness_keys
                    if source_designator in resolved_source_designators
                ),
            )
        except finite_evaluator.FiniteEvaluatorLiftError as exc:
            raise ValueError(
                "Finite evaluator induction failed for the resolved source selection."
            ) from exc
    return Evaluator(
        declared_conditions=tuple(
            _profile_condition_from_carrier_declared_condition(
                declared_condition=declared_condition,
                resolved_source_designators=resolved_source_designators,
                provider_witness_keys=provider_witness_keys,
            )
            for declared_condition in evaluator_carrier.declared_conditions
        )
    )


def _profile_condition_from_carrier_declared_condition(
    *,
    declared_condition: DeclaredCondition,
    resolved_source_designators: frozenset[tuple[str, str, str]],
    provider_witness_keys: frozenset[tuple[tuple[str, str, str], str]],
) -> ProfileCondition:
    payload = reference_profile_parameter_value(
        parameters=declared_condition.parameters,
        identifier=DECLARATION_PARAMETER,
    )
    if not isinstance(payload, dict):
        raise ValueError(
            "declared condition is missing reference-profile declaration payload: "
            f"{declared_condition.condition_identifier!s}."
        )
    declaration = reference_profile_declaration_from_payload(
        condition_identifier=str(declared_condition.condition_identifier),
        payload=payload,
    )
    return ProfileCondition(
        condition_id=CoreConditionId(str(declaration.condition_id)),
        determining_semantics=_condition_semantics(
            condition_identifier=str(declared_condition.condition_identifier),
            source_designator=declared_condition.determining_source_designator,
            resolved_source_designators=resolved_source_designators,
            provider_witness_keys=provider_witness_keys,
        ),
        profile_declaration=declaration,
    )


def _resolved_source_designators(
    *,
    referenced_sources: tuple[ResolvedReferencedSource, ...],
) -> frozenset[tuple[str, str, str]]:
    return frozenset(
        _evaluator_lifting_designator_key(
            designator=referenced_source.verified_source.immutable_designator
        )
        for referenced_source in referenced_sources
    )


def _provider_witness_keys(
    *,
    provider_witnesses: tuple[object, ...],
) -> frozenset[tuple[tuple[str, str, str], str]]:
    return frozenset(
        (
            _evaluator_lifting_designator_key(
                designator=getattr(witness, "source_designator", None)
            ),
            _semantics_key_text(witness=witness),
        )
        for witness in provider_witnesses
    )


def _semantics_key_text(*, witness: object) -> str:
    semantics_key = getattr(witness, "semantics_key", None)
    if not isinstance(semantics_key, str) or not semantics_key:
        raise ValueError("provider witness semantics_key must be text.")
    return semantics_key


def _evaluator_lifting_designator_key(
    *,
    designator: object,
) -> tuple[str, str, str]:
    digest = getattr(designator, "digest", None)
    algorithm_id = getattr(digest, "algorithm_id", None)
    digest_value = getattr(digest, "digest_value", None)
    uri = getattr(designator, "uri", None)
    if not isinstance(uri, str):
        raise ValueError("immutable source designator uri must be text.")
    if not isinstance(algorithm_id, str):
        raise ValueError("immutable source designator digest algorithm must be text.")
    if not isinstance(digest_value, str):
        raise ValueError("immutable source designator digest value must be text.")
    return (uri, algorithm_id, digest_value)


def _condition_semantics(
    *,
    condition_identifier: str,
    source_designator: object | None,
    resolved_source_designators: frozenset[tuple[str, str, str]],
    provider_witness_keys: frozenset[tuple[tuple[str, str, str], str]],
) -> ConditionSemantics:
    try:
        binding = reference_profile_condition_semantics_binding(
            condition_id=ProfileConditionId(condition_identifier)
        )
    except ValueError:
        return UnrecoverableConditionSemantics()
    if binding is None:
        return UndesignatedConditionSemantics()
    if source_designator is None:
        return UndesignatedConditionSemantics()
    source_designator_key = _evaluator_lifting_designator_key(
        designator=source_designator
    )
    if source_designator_key not in resolved_source_designators:
        raise ValueError(
            "declared condition semantics cannot be resolved without a verified "
            f"exact-edition source binding: {condition_identifier}."
        )
    provider_witness_key = (source_designator_key, str(binding.semantics_key))
    if provider_witness_key not in provider_witness_keys:
        raise ValueError(
            "declared condition semantics cannot be resolved without a provider "
            f"witness for exact-edition source binding: {condition_identifier}."
        )
    return ResolvedConditionSemantics(semantics_key=binding.semantics_key)
