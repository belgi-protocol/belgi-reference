from __future__ import annotations

from belgi.carrier import (
    BindingKindIdentifier,
    ConditionIdentifier,
    DeclaredCondition,
    Digest,
    EvaluatorCarrier,
    EvidenceConditionBindingDeclaration,
    EvidenceIdentifier,
    ImmutableDesignator,
    ReplayPolicyIdentifier,
    TrustBoundaryDeclaration,
    TrustBoundaryIdentifier,
)
from belgi.carrier.json_representation import TrustedJSONRole
from belgi.replay.lifting.exceptions import ParseFailureError
from belgi.replay.lifting.parsing import (
    load_trusted_carrier_json_object,
    require_string,
)
from belgi.replay.parsing import (
    parse_declaration_parameters,
    require_json_mapping,
)

__all__ = ["parse_evaluator_carrier"]


def _evaluator_designator_from_payload(
    *,
    payload: object | None,
    description: str,
) -> ImmutableDesignator | None:
    if payload is None:
        return None
    designator = require_json_mapping(value=payload, description=description)
    digest = require_json_mapping(
        value=designator.get("digest"),
        description=f"{description}.digest",
    )
    return ImmutableDesignator(
        uri=require_string(obj=designator, key="uri", description=description),
        digest=Digest(
            algorithm_id=require_string(
                obj=digest,
                key="algorithmId",
                description=f"{description}.digest",
            ),
            digest_value=require_string(
                obj=digest,
                key="digestValue",
                description=f"{description}.digest",
            ),
        ),
    )


def _evaluator_designator_list_from_payload(
    *,
    payload: object | None,
    description: str,
) -> tuple[ImmutableDesignator, ...]:
    if payload is None:
        return ()
    if not isinstance(payload, list):
        raise ParseFailureError(message=f"{description} must be a JSON array")
    designators: list[ImmutableDesignator] = []
    seen: set[ImmutableDesignator] = set()
    for index, raw_designator in enumerate(payload):
        designator = _evaluator_designator_from_payload(
            payload=raw_designator,
            description=f"{description}[{index}]",
        )
        if designator is None:
            raise ParseFailureError(
                message=f"{description}[{index}] must be an immutable designator object",
            )
        if designator in seen:
            raise ParseFailureError(
                message=f"{description} contains duplicate designator {designator!s}",
            )
        seen.add(designator)
        designators.append(designator)
    return tuple(designators)


def _evaluator_required_string_list(
    *,
    payload: object | None,
    description: str,
) -> tuple[str, ...]:
    if not isinstance(payload, list):
        raise ParseFailureError(message=f"{description} must be a JSON array")
    if not payload:
        raise ParseFailureError(message=f"{description} must not be empty")
    values: list[str] = []
    seen: set[str] = set()
    for index, raw_value in enumerate(payload):
        if not isinstance(raw_value, str) or not raw_value:
            raise ParseFailureError(
                message=f"{description}[{index}] must be a non-empty string",
            )
        if raw_value in seen:
            raise ParseFailureError(
                message=f"{description} contains duplicate value {raw_value!r}",
            )
        seen.add(raw_value)
        values.append(raw_value)
    return tuple(values)


def _evaluator_trust_boundaries_from_payload(
    *,
    payload: object | None,
    description: str,
) -> tuple[TrustBoundaryDeclaration, ...]:
    trust_boundaries_payload = require_json_mapping(
        value=payload,
        description=description,
    )
    return tuple(
        TrustBoundaryDeclaration(
            boundary_identifier=TrustBoundaryIdentifier(boundary_identifier),
            parameters=parse_declaration_parameters(
                payload=require_json_mapping(
                    value=trust_boundary_payload,
                    description=f"{description}.{boundary_identifier}",
                ).get("parameters"),
                description=f"{description}.{boundary_identifier}.parameters",
            ),
        )
        for boundary_identifier, trust_boundary_payload in sorted(
            trust_boundaries_payload.items()
        )
    )


def _evaluator_evidence_condition_bindings_from_payload(
    *,
    payload: object | None,
    description: str,
) -> tuple[EvidenceConditionBindingDeclaration, ...]:
    evidence_condition_bindings_payload = require_json_mapping(
        value=payload,
        description=description,
    )
    bindings: list[EvidenceConditionBindingDeclaration] = []
    for condition_identifier, raw_bindings in sorted(
        evidence_condition_bindings_payload.items()
    ):
        if not isinstance(raw_bindings, list):
            raise ParseFailureError(
                message=f"{description}.{condition_identifier} must be a JSON array",
            )
        if not raw_bindings:
            raise ParseFailureError(
                message=f"{description}.{condition_identifier} must not be empty",
            )
        for index, raw_binding in enumerate(raw_bindings):
            binding = require_json_mapping(
                value=raw_binding,
                description=f"{description}.{condition_identifier}[{index}]",
            )
            bindings.append(
                EvidenceConditionBindingDeclaration(
                    binding_kind_identifier=BindingKindIdentifier(
                        require_string(
                            obj=binding,
                            key="bindingKindIdentifier",
                            description=f"{description}.{condition_identifier}[{index}]",
                        )
                    ),
                    condition_identifier=ConditionIdentifier(condition_identifier),
                    evidence_identifiers=tuple(
                        EvidenceIdentifier(evidence_identifier)
                        for evidence_identifier in _evaluator_required_string_list(
                            payload=binding.get("evidenceIdentifiers"),
                            description=(
                                f"{description}.{condition_identifier}[{index}]."
                                "evidenceIdentifiers"
                            ),
                        )
                    ),
                    parameters=parse_declaration_parameters(
                        payload=binding.get("parameters"),
                        description=(
                            f"{description}.{condition_identifier}[{index}].parameters"
                        ),
                    ),
                )
            )
    return tuple(bindings)


def parse_evaluator_carrier(
    *,
    root_bytes: bytes,
    description: str,
) -> EvaluatorCarrier:
    payload = load_trusted_carrier_json_object(
        octets=root_bytes,
        description=description,
        trusted_role=TrustedJSONRole.EVALUATOR,
    )
    declared_conditions_payload = require_json_mapping(
        value=payload.get("declaredConditions"),
        description=f"{description}.declaredConditions",
    )
    declared_conditions = tuple(
        DeclaredCondition(
            condition_identifier=ConditionIdentifier(condition_identifier),
            parameters=parse_declaration_parameters(
                payload=require_json_mapping(
                    value=condition_payload,
                    description=f"{description}.declaredConditions.{condition_identifier}",
                ).get("parameters"),
                description=f"{description}.declaredConditions.{condition_identifier}.parameters",
            ),
            determining_source_designator=_evaluator_designator_from_payload(
                payload=require_json_mapping(
                    value=condition_payload,
                    description=f"{description}.declaredConditions.{condition_identifier}",
                ).get("determiningSourceDesignator"),
                description=f"{description}.declaredConditions.{condition_identifier}.determiningSourceDesignator",
            ),
        )
        for condition_identifier, condition_payload in sorted(
            declared_conditions_payload.items()
        )
    )
    return EvaluatorCarrier(
        declared_conditions=declared_conditions,
        replay_policy_identifier=(
            None
            if payload.get("replayPolicy") is None
            else ReplayPolicyIdentifier(
                require_string(
                    obj=payload,
                    key="replayPolicy",
                    description=description,
                )
            )
        ),
        trust_boundaries=_evaluator_trust_boundaries_from_payload(
            payload=payload.get("trustBoundaries"),
            description=f"{description}.trustBoundaries",
        ),
        governing_specification_designators=_evaluator_designator_list_from_payload(
            payload=payload.get("governingSpecificationDesignators"),
            description=f"{description}.governingSpecificationDesignators",
        ),
        exact_edition_designators=_evaluator_designator_list_from_payload(
            payload=payload.get("exactEditionDesignators"),
            description=f"{description}.exactEditionDesignators",
        ),
        evidence_condition_bindings=_evaluator_evidence_condition_bindings_from_payload(
            payload=payload.get("evidenceConditionBindings"),
            description=f"{description}.evidenceConditionBindings",
        ),
    )
