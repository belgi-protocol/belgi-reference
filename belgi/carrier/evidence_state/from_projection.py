from __future__ import annotations

from collections.abc import Iterable, Mapping

from belgi.carrier.exceptions import EvidenceCarrierError
from belgi.carrier.inventory import (
    ContentLocator,
    DeclarationParameter,
    JsonCompatible,
    ParameterIdentifier,
)

from .carrier import (
    EvidenceIdentifier,
    EvidenceItem,
    EvidenceKindIdentifier,
    EvidenceStateCarrier,
)

__all__ = ["evidence_state_carrier_from_projection"]


def evidence_state_carrier_from_projection(
    *,
    carrier_projection: object,
) -> EvidenceStateCarrier:
    evidence_items = getattr(carrier_projection, "evidence_items", None)
    if (
        evidence_items is None
        or isinstance(evidence_items, (str, bytes, bytearray))
        or not isinstance(evidence_items, Iterable)
    ):
        raise EvidenceCarrierError("carrier_projection.evidence_items is required.")
    return EvidenceStateCarrier(
        evidence_items=tuple(
            _evidence_item_from_projection_item(
                item=item,
                ordinal=ordinal,
            )
            for ordinal, item in enumerate(evidence_items, start=1)
        )
    )


def _evidence_item_from_projection_item(
    *,
    item: object,
    ordinal: int,
) -> EvidenceItem:
    label = f"carrier_projection.evidence_items[{ordinal}]"
    evidence_identifier = _required_projection_text(
        item=item,
        attribute="evidence_identifier",
        label=label,
    )
    evidence_kind_identifier = _required_projection_text(
        item=item,
        attribute="evidence_kind_identifier",
        label=label,
    )
    media_type = _required_projection_text(
        item=item,
        attribute="media_type",
        label=label,
    )
    source_content = _require_evidence_projection_json(
        value=getattr(item, "source_content", None),
        label=f"{label}.source_content",
    )
    parameters = getattr(item, "parameters", ())
    if (
        parameters is None
        or isinstance(parameters, (str, bytes, bytearray))
        or not isinstance(parameters, Iterable)
    ):
        raise EvidenceCarrierError(f"{label}.parameters must be iterable.")
    return EvidenceItem(
        evidence_identifier=EvidenceIdentifier(evidence_identifier),
        evidence_kind_identifier=EvidenceKindIdentifier(evidence_kind_identifier),
        source=ContentLocator.inline_value(
            media_type=media_type,
            value=source_content,
        ),
        parameters=tuple(
            _declaration_parameter_from_projection_parameter(
                parameter=parameter,
                label=f"{label}.parameters[{parameter_ordinal}]",
            )
            for parameter_ordinal, parameter in enumerate(parameters, start=1)
        ),
    )


def _declaration_parameter_from_projection_parameter(
    *,
    parameter: object,
    label: str,
) -> DeclarationParameter:
    parameter_identifier = getattr(parameter, "parameter_identifier", None)
    if not isinstance(parameter_identifier, str) or not parameter_identifier:
        raise EvidenceCarrierError(
            f"{label}.parameter_identifier must be a non-empty string."
        )
    return DeclarationParameter.from_value(
        parameter_identifier=ParameterIdentifier(parameter_identifier),
        value=_require_evidence_projection_json(
            value=getattr(parameter, "value", None),
            label=f"{label}.value",
        ),
    )


def _required_projection_text(
    *,
    item: object,
    attribute: str,
    label: str,
) -> str:
    value = getattr(item, attribute, None)
    if not isinstance(value, str) or not value:
        raise EvidenceCarrierError(f"{label}.{attribute} must be a non-empty string.")
    return value


def _require_evidence_projection_json(
    *,
    value: object,
    label: str,
) -> JsonCompatible:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        return [
            _require_evidence_projection_json(value=item, label=f"{label}[]")
            for item in value
        ]
    if isinstance(value, Mapping):
        converted: dict[str, JsonCompatible] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise EvidenceCarrierError(f"{label} must use string object keys.")
            converted[key] = _require_evidence_projection_json(
                value=item,
                label=f"{label}.{key}",
            )
        return converted
    raise EvidenceCarrierError(f"{label} must contain only JSON-compatible values.")
