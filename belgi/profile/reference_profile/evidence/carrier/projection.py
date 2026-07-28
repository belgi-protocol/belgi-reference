from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TypeAlias

from belgi.core import EvidenceState
from belgi.profile.reference_profile.declarations.source import (
    ALL_GENERIC_EVIDENCE_SOURCE_CLASSES,
)
from belgi.profile.reference_profile.evidence.carrier.parameters import (
    EVIDENCE_APPROVAL_COUNT_PARAMETER,
    EVIDENCE_AUTHORITY_LEVEL_PARAMETER,
    EVIDENCE_BLOCKING_COUNT_PARAMETER,
    EVIDENCE_BOUNDARY_PARTICIPATION_PARAMETER,
    EVIDENCE_EQUIVALENCE_BASIS_PARAMETER,
    EVIDENCE_FAILURE_COUNT_PARAMETER,
    EVIDENCE_NUMERIC_VALUE_PARAMETER,
    EVIDENCE_OUTCOME_PARAMETER,
    EVIDENCE_SEVERITY_PARAMETER,
    EVIDENCE_SOURCE_CLASS_PARAMETER,
)
from belgi.profile.reference_profile.evidence.item import ReferenceProfileEvidenceItem
from belgi.profile.reference_profile.evidence.review_record import (
    PART4_EVIDENCE_SOURCE_CLASS_PARAMETER,
    REVIEW_RECORD_IDENTIFIER,
    normalize_reference_profile_review_record,
)
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvidenceStateCompileError,
)

__all__ = [
    "JsonCompatible",
    "ReferenceProfileCarrierAlignedEvidenceItem",
    "ReferenceProfileCarrierAlignedEvidenceParameter",
    "ReferenceProfileCarrierAlignedEvidenceState",
    "reference_profile_aligned_evidence_state_carrier",
]


JsonScalar: TypeAlias = None | bool | int | float | str
JsonCompatible: TypeAlias = (
    JsonScalar | list["JsonCompatible"] | dict[str, "JsonCompatible"]
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileCarrierAlignedEvidenceParameter:
    parameter_identifier: str
    value: JsonCompatible


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileCarrierAlignedEvidenceItem:
    evidence_identifier: str
    evidence_kind_identifier: str
    media_type: str
    source_content: dict[str, JsonCompatible]
    parameters: tuple[ReferenceProfileCarrierAlignedEvidenceParameter, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileCarrierAlignedEvidenceState:
    evidence_items: tuple[ReferenceProfileCarrierAlignedEvidenceItem, ...]


def reference_profile_aligned_evidence_state_carrier(
    *,
    evidence_state: object,
) -> ReferenceProfileCarrierAlignedEvidenceState:
    if not isinstance(evidence_state, EvidenceState):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_carrier_projection",
            detail="evidence carrier projection requires a core EvidenceState.",
        )
    return ReferenceProfileCarrierAlignedEvidenceState(
        evidence_items=tuple(
            _aligned_evidence_item(item=item, ordinal=ordinal)
            for ordinal, item in enumerate(evidence_state.items, start=1)
        ),
    )


def _aligned_evidence_item(
    *,
    item: object,
    ordinal: int,
) -> ReferenceProfileCarrierAlignedEvidenceItem:
    label = f"evidence_state.items[{ordinal}]"
    if not isinstance(item, ReferenceProfileEvidenceItem):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_carrier_projection",
            detail=(
                f"{label} must be a ReferenceProfileEvidenceItem before "
                "reference-profile carrier projection can preserve it."
            ),
        )
    source_content = _evidence_projection_json_mapping(
        value=item.subject,
        label=f"{label}.subject",
    )
    _validate_optional_subject_identifier(
        source_content=source_content,
        key="evidenceKindIdentifier",
        expected=item.kind,
        label=label,
    )
    if item.kind == REVIEW_RECORD_IDENTIFIER:
        source_content = _strict_review_projection_source_content(
            item=item,
            source_content=source_content,
            label=label,
        )
    return ReferenceProfileCarrierAlignedEvidenceItem(
        evidence_identifier=_required_subject_non_empty_text(
            value=item.identifier,
            label=f"{label}.identifier",
        ),
        evidence_kind_identifier=_required_subject_non_empty_text(
            value=item.kind,
            label=f"{label}.kind",
        ),
        media_type="application/json",
        source_content=source_content,
        parameters=_semantic_parameters(item=item, label=label),
    )


def _semantic_parameters(
    *,
    item: ReferenceProfileEvidenceItem,
    label: str,
) -> tuple[ReferenceProfileCarrierAlignedEvidenceParameter, ...]:
    if item.kind == REVIEW_RECORD_IDENTIFIER:
        source_class = _required_subject_non_empty_text(
            value=item.source_class,
            label=f"{label}.source_class",
        )
        return (
            ReferenceProfileCarrierAlignedEvidenceParameter(
                parameter_identifier=PART4_EVIDENCE_SOURCE_CLASS_PARAMETER,
                value=source_class,
            ),
        )
    parameters: list[ReferenceProfileCarrierAlignedEvidenceParameter] = []
    _append_optional_parameter(
        parameters=parameters,
        parameter_identifier=EVIDENCE_SOURCE_CLASS_PARAMETER,
        value=item.source_class,
        label=label,
    )
    _append_optional_parameter(
        parameters=parameters,
        parameter_identifier=EVIDENCE_BOUNDARY_PARTICIPATION_PARAMETER,
        value=item.boundary_participation,
        label=label,
    )
    _append_optional_parameter(
        parameters=parameters,
        parameter_identifier=EVIDENCE_AUTHORITY_LEVEL_PARAMETER,
        value=item.authority_level,
        label=label,
    )
    _append_optional_parameter(
        parameters=parameters,
        parameter_identifier=EVIDENCE_OUTCOME_PARAMETER,
        value=item.outcome,
        label=label,
    )
    _append_optional_parameter(
        parameters=parameters,
        parameter_identifier=EVIDENCE_NUMERIC_VALUE_PARAMETER,
        value=item.numeric_value,
        label=label,
    )
    _append_optional_parameter(
        parameters=parameters,
        parameter_identifier=EVIDENCE_SEVERITY_PARAMETER,
        value=item.severity,
        label=label,
    )
    _append_optional_parameter(
        parameters=parameters,
        parameter_identifier=EVIDENCE_FAILURE_COUNT_PARAMETER,
        value=item.failure_count,
        label=label,
    )
    _append_optional_parameter(
        parameters=parameters,
        parameter_identifier=EVIDENCE_APPROVAL_COUNT_PARAMETER,
        value=item.approval_count,
        label=label,
    )
    _append_optional_parameter(
        parameters=parameters,
        parameter_identifier=EVIDENCE_BLOCKING_COUNT_PARAMETER,
        value=item.blocking_count,
        label=label,
    )
    _append_optional_parameter(
        parameters=parameters,
        parameter_identifier=EVIDENCE_EQUIVALENCE_BASIS_PARAMETER,
        value=item.equivalence_basis,
        label=label,
    )
    return tuple(parameters)


def _strict_review_projection_source_content(
    *,
    item: ReferenceProfileEvidenceItem,
    source_content: dict[str, JsonCompatible],
    label: str,
) -> dict[str, JsonCompatible]:
    try:
        review_record = normalize_reference_profile_review_record(
            document=source_content,
            label=f"{label}.subject",
        )
    except ValueError as exc:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_carrier_projection",
            detail=str(exc),
        ) from exc
    recognized_source_classes = frozenset(
        str(source_class) for source_class in ALL_GENERIC_EVIDENCE_SOURCE_CLASSES
    )
    if item.source_class not in recognized_source_classes:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_carrier_projection",
            detail=f"{label}.source_class is not a Part 4 source class.",
        )
    forbidden_fields = (
        "boundary_participation",
        "authority_level",
        "outcome",
        "numeric_value",
        "severity",
        "failure_count",
        "approval_count",
        "blocking_count",
        "environment_terms",
        "equivalence_basis",
    )
    populated = tuple(
        field_name
        for field_name in forbidden_fields
        if getattr(item, field_name) is not None
    )
    if populated:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_carrier_projection",
            detail=(
                f"{label} strict ReviewRecord carries unsupported semantic "
                f"fields: {', '.join(populated)}."
            ),
        )
    return dict(review_record)


def _append_optional_parameter(
    *,
    parameters: list[ReferenceProfileCarrierAlignedEvidenceParameter],
    parameter_identifier: str,
    value: object,
    label: str,
) -> None:
    if value is None:
        return
    parameters.append(
        ReferenceProfileCarrierAlignedEvidenceParameter(
            parameter_identifier=parameter_identifier,
            value=_evidence_projection_json_value(
                value=value,
                label=f"{label}.{parameter_identifier}",
            ),
        )
    )


def _validate_optional_subject_identifier(
    *,
    source_content: Mapping[str, JsonCompatible],
    key: str,
    expected: str,
    label: str,
) -> None:
    value = source_content.get(key)
    if value is None:
        return
    if value != expected:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_carrier_projection",
            detail=f"{label}.subject.{key} must match the semantic item kind.",
        )


def _required_subject_non_empty_text(
    *,
    value: object,
    label: str,
) -> str:
    if not isinstance(value, str) or not value:
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_carrier_projection",
            detail=f"{label} must be a non-empty string.",
        )
    return value


def _evidence_projection_json_mapping(
    *,
    value: object,
    label: str,
) -> dict[str, JsonCompatible]:
    converted = _evidence_projection_json_value(value=value, label=label)
    if not isinstance(converted, dict):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice="evidence_carrier_projection",
            detail=f"{label} must be a JSON object.",
        )
    return converted


def _evidence_projection_json_value(
    *,
    value: object,
    label: str,
) -> JsonCompatible:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Mapping):
        converted: dict[str, JsonCompatible] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ReferenceProfileEvidenceStateCompileError(
                    semantic_slice="evidence_carrier_projection",
                    detail=f"{label} must use string object keys.",
                )
            converted[key] = _evidence_projection_json_value(
                value=item,
                label=f"{label}.{key}",
            )
        return converted
    if isinstance(value, tuple):
        if all(_evidence_projection_frozen_mapping_item(item=item) for item in value):
            return {
                key: _evidence_projection_json_value(
                    value=item_value,
                    label=f"{label}.{key}",
                )
                for key, item_value in value
            }
        return [
            _evidence_projection_json_value(value=item, label=f"{label}[]")
            for item in value
        ]
    if isinstance(value, list):
        return [
            _evidence_projection_json_value(value=item, label=f"{label}[]")
            for item in value
        ]
    raise ReferenceProfileEvidenceStateCompileError(
        semantic_slice="evidence_carrier_projection",
        detail=f"{label} must contain only JSON-compatible values.",
    )


def _evidence_projection_frozen_mapping_item(*, item: object) -> bool:
    return isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str)
