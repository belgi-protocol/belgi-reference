from __future__ import annotations

from collections.abc import Iterable, Mapping

from belgi.carrier.evidence_state import EvidenceIdentifier
from belgi.carrier.exceptions import EvaluatorCarrierError
from belgi.carrier.inventory import (
    DeclarationParameter,
    ImmutableDesignator,
    JsonCompatible,
    ParameterIdentifier,
)

from .carrier import (
    BindingKindIdentifier,
    ConditionIdentifier,
    DeclaredCondition,
    EvaluatorCarrier,
    EvidenceConditionBindingDeclaration,
    ReplayPolicyIdentifier,
    TrustBoundaryDeclaration,
    TrustBoundaryIdentifier,
)

__all__ = ["evaluator_carrier_from_projection"]


def evaluator_carrier_from_projection(
    *,
    carrier_projection: object,
) -> EvaluatorCarrier:
    replay_policy_identifier = getattr(
        carrier_projection,
        "replay_policy_identifier",
        None,
    )
    return EvaluatorCarrier(
        declared_conditions=tuple(
            _evaluator_declared_condition_from_projection(
                item=item,
                ordinal=ordinal,
            )
            for ordinal, item in enumerate(
                _evaluator_projection_sequence(
                    carrier_projection=carrier_projection,
                    attribute="declared_conditions",
                ),
                start=1,
            )
        ),
        replay_policy_identifier=(
            None
            if replay_policy_identifier is None
            else ReplayPolicyIdentifier(
                _required_evaluator_projection_text_value(
                    value=replay_policy_identifier,
                    label="carrier_projection.replay_policy_identifier",
                )
            )
        ),
        trust_boundaries=tuple(
            _evaluator_trust_boundary_from_projection(
                item=item,
                ordinal=ordinal,
            )
            for ordinal, item in enumerate(
                _evaluator_projection_sequence(
                    carrier_projection=carrier_projection,
                    attribute="trust_boundaries",
                ),
                start=1,
            )
        ),
        exact_edition_designators=tuple(
            _evaluator_projection_designator(
                value=item,
                label=f"carrier_projection.exact_edition_designators[{ordinal}]",
            )
            for ordinal, item in enumerate(
                _evaluator_projection_sequence(
                    carrier_projection=carrier_projection,
                    attribute="exact_edition_designators",
                ),
                start=1,
            )
        ),
        evidence_condition_bindings=tuple(
            _evaluator_evidence_condition_binding_from_projection(
                item=item,
                ordinal=ordinal,
            )
            for ordinal, item in enumerate(
                _evaluator_projection_sequence(
                    carrier_projection=carrier_projection,
                    attribute="evidence_condition_bindings",
                ),
                start=1,
            )
        ),
    )


def _evaluator_declared_condition_from_projection(
    *,
    item: object,
    ordinal: int,
) -> DeclaredCondition:
    label = f"carrier_projection.declared_conditions[{ordinal}]"
    determining_source_designator = getattr(item, "determining_source_designator", None)
    if determining_source_designator is not None:
        determining_source_designator = _evaluator_projection_designator(
            value=determining_source_designator,
            label=f"{label}.determining_source_designator",
        )
    return DeclaredCondition(
        condition_identifier=ConditionIdentifier(
            _required_evaluator_projection_text(
                item=item,
                attribute="condition_identifier",
                label=label,
            )
        ),
        parameters=_evaluator_projection_parameters(
            item=item,
            label=label,
        ),
        determining_source_designator=determining_source_designator,
    )


def _evaluator_trust_boundary_from_projection(
    *,
    item: object,
    ordinal: int,
) -> TrustBoundaryDeclaration:
    label = f"carrier_projection.trust_boundaries[{ordinal}]"
    return TrustBoundaryDeclaration(
        boundary_identifier=TrustBoundaryIdentifier(
            _required_evaluator_projection_text(
                item=item,
                attribute="boundary_identifier",
                label=label,
            )
        ),
        parameters=_evaluator_projection_parameters(
            item=item,
            label=label,
        ),
    )


def _evaluator_evidence_condition_binding_from_projection(
    *,
    item: object,
    ordinal: int,
) -> EvidenceConditionBindingDeclaration:
    label = f"carrier_projection.evidence_condition_bindings[{ordinal}]"
    return EvidenceConditionBindingDeclaration(
        binding_kind_identifier=BindingKindIdentifier(
            _required_evaluator_projection_text(
                item=item,
                attribute="binding_kind_identifier",
                label=label,
            )
        ),
        condition_identifier=ConditionIdentifier(
            _required_evaluator_projection_text(
                item=item,
                attribute="condition_identifier",
                label=label,
            )
        ),
        evidence_identifiers=tuple(
            EvidenceIdentifier(
                _required_evaluator_projection_text_value(
                    value=value,
                    label=f"{label}.evidence_identifiers[{value_ordinal}]",
                )
            )
            for value_ordinal, value in enumerate(
                _evaluator_projection_attribute_sequence(
                    item=item,
                    attribute="evidence_identifiers",
                    label=label,
                ),
                start=1,
            )
        ),
        parameters=_evaluator_projection_parameters(
            item=item,
            label=label,
        ),
    )


def _evaluator_projection_parameters(
    *,
    item: object,
    label: str,
) -> tuple[DeclarationParameter, ...]:
    return tuple(
        _evaluator_declaration_parameter_from_projection_parameter(
            parameter=parameter,
            label=f"{label}.parameters[{parameter_ordinal}]",
        )
        for parameter_ordinal, parameter in enumerate(
            _evaluator_projection_attribute_sequence(
                item=item,
                attribute="parameters",
                label=label,
            ),
            start=1,
        )
    )


def _evaluator_declaration_parameter_from_projection_parameter(
    *,
    parameter: object,
    label: str,
) -> DeclarationParameter:
    return DeclarationParameter.from_value(
        parameter_identifier=ParameterIdentifier(
            _required_evaluator_projection_text(
                item=parameter,
                attribute="parameter_identifier",
                label=label,
            )
        ),
        value=_require_evaluator_projection_json(
            value=getattr(parameter, "value", None),
            label=f"{label}.value",
        ),
    )


def _evaluator_projection_sequence(
    *,
    carrier_projection: object,
    attribute: str,
) -> tuple[object, ...]:
    return _evaluator_projection_attribute_sequence(
        item=carrier_projection,
        attribute=attribute,
        label="carrier_projection",
    )


def _evaluator_projection_attribute_sequence(
    *,
    item: object,
    attribute: str,
    label: str,
) -> tuple[object, ...]:
    value = getattr(item, attribute, None)
    if value is None:
        raise EvaluatorCarrierError(f"{label}.{attribute} is required.")
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Iterable):
        raise EvaluatorCarrierError(f"{label}.{attribute} must be iterable.")
    return tuple(value)


def _required_evaluator_projection_text(
    *,
    item: object,
    attribute: str,
    label: str,
) -> str:
    return _required_evaluator_projection_text_value(
        value=getattr(item, attribute, None),
        label=f"{label}.{attribute}",
    )


def _required_evaluator_projection_text_value(
    *,
    value: object,
    label: str,
) -> str:
    if not isinstance(value, str) or not value:
        raise EvaluatorCarrierError(f"{label} must be a non-empty string.")
    return value


def _evaluator_projection_designator(
    *,
    value: object,
    label: str,
) -> ImmutableDesignator:
    if isinstance(value, ImmutableDesignator):
        return value
    uri = getattr(value, "uri", None)
    digest = getattr(value, "digest", None)
    algorithm_id = getattr(digest, "algorithm_id", None)
    digest_value = getattr(digest, "digest_value", None)
    if not isinstance(uri, str) or not uri:
        raise EvaluatorCarrierError(f"{label}.uri must be a non-empty string.")
    if not isinstance(algorithm_id, str) or not algorithm_id:
        raise EvaluatorCarrierError(
            f"{label}.digest.algorithm_id must be a non-empty string."
        )
    if not isinstance(digest_value, str) or not digest_value:
        raise EvaluatorCarrierError(
            f"{label}.digest.digest_value must be a non-empty string."
        )
    from belgi.carrier.inventory import Digest

    return ImmutableDesignator(
        uri=uri,
        digest=Digest(
            algorithm_id=algorithm_id,
            digest_value=digest_value,
        ),
    )


def _require_evaluator_projection_json(
    *,
    value: object,
    label: str,
) -> JsonCompatible:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        return [
            _require_evaluator_projection_json(value=item, label=f"{label}[]")
            for item in value
        ]
    if isinstance(value, Mapping):
        converted: dict[str, JsonCompatible] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise EvaluatorCarrierError(f"{label} must use string object keys.")
            converted[key] = _require_evaluator_projection_json(
                value=item,
                label=f"{label}.{key}",
            )
        return converted
    raise EvaluatorCarrierError(f"{label} must contain only JSON-compatible values.")
