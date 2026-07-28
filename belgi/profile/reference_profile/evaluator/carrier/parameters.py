from __future__ import annotations

import math
from typing import TypeAlias

from belgi.profile.vocabulary.tolerances import SeverityLevel

__all__ = [
    "ALLOWED_SOURCE_CLASSES_PARAMETER",
    "AUTHORITY_LEVEL_PARAMETER",
    "BOUNDARY_PARTICIPATION_PARAMETER",
    "DECLARATION_PARAMETER",
    "EVIDENCE_KIND_PARAMETER",
    "MINIMUM_AUTHORITY_PARAMETER",
    "MINIMUM_COUNT_PARAMETER",
    "JsonCompatible",
    "reference_profile_optional_int_payload",
    "reference_profile_optional_numeric_payload",
    "reference_profile_optional_severity_payload",
    "reference_profile_parameter_value",
    "reference_profile_required_bool_payload",
    "reference_profile_required_int_payload",
    "reference_profile_required_string_payload",
    "reference_profile_required_string_tuple_payload",
]


JsonScalar: TypeAlias = None | bool | int | float | str
JsonCompatible: TypeAlias = (
    JsonScalar | list["JsonCompatible"] | dict[str, "JsonCompatible"]
)

DECLARATION_PARAMETER = "belgi.reference-profile.parameter.profile-declaration"
BOUNDARY_PARTICIPATION_PARAMETER = (
    "belgi.reference-profile.parameter.boundary-participation"
)
AUTHORITY_LEVEL_PARAMETER = "belgi.reference-profile.parameter.authority-level"
EVIDENCE_KIND_PARAMETER = "belgi.reference-profile.parameter.evidence-kind"
MINIMUM_COUNT_PARAMETER = "belgi.reference-profile.parameter.minimum-count"
MINIMUM_AUTHORITY_PARAMETER = "belgi.reference-profile.parameter.minimum-authority"
ALLOWED_SOURCE_CLASSES_PARAMETER = (
    "belgi.reference-profile.parameter.allowed-source-classes"
)


def reference_profile_parameter_value(
    *,
    parameters: tuple[object, ...],
    identifier: str,
) -> JsonCompatible | None:
    for parameter in parameters:
        parameter_identifier = getattr(parameter, "parameter_identifier", None)
        if str(parameter_identifier) != identifier:
            continue
        value = getattr(parameter, "value", None)
        if value is None:
            return None
        to_compatible_value = getattr(value, "to_compatible_value", None)
        if not callable(to_compatible_value):
            return None
        compatible_value = to_compatible_value()
        return _reference_profile_json_compatible(
            value=compatible_value,
            label=f"declaration parameter {identifier}",
        )
    return None


def _reference_profile_json_compatible(
    *,
    value: object,
    label: str,
) -> JsonCompatible:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"{label} numbers must be finite.")
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        return [
            _reference_profile_json_compatible(value=item, label=f"{label}[]")
            for item in value
        ]
    if isinstance(value, dict):
        converted: dict[str, JsonCompatible] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{label} must use string object keys.")
            converted[key] = _reference_profile_json_compatible(
                value=item,
                label=f"{label}.{key}",
            )
        return converted
    raise ValueError(f"{label} must be JSON-compatible.")


def reference_profile_required_string_tuple_payload(
    *,
    payload: object,
) -> tuple[str, ...]:
    if not isinstance(payload, list):
        raise ValueError("expected string-list payload.")
    values: list[str] = []
    for item in payload:
        if not isinstance(item, str):
            raise ValueError("expected string list payload.")
        values.append(item)
    return tuple(values)


def reference_profile_optional_numeric_payload(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("expected finite numeric payload.")
    try:
        normalized = float(value)
    except OverflowError as exc:
        raise ValueError("expected finite numeric payload.") from exc
    if not math.isfinite(normalized):
        raise ValueError("expected finite numeric payload.")
    return normalized


def reference_profile_optional_int_payload(value: object) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("expected integer payload.")
    return value


def reference_profile_required_int_payload(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError("expected integer payload.")
    return value


def reference_profile_required_bool_payload(value: object) -> bool:
    if not isinstance(value, bool):
        raise ValueError("expected boolean payload.")
    return value


def reference_profile_required_string_payload(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("expected string payload.")
    return value


def reference_profile_optional_severity_payload(
    value: object,
) -> SeverityLevel | None:
    if value is None:
        return None
    return SeverityLevel(reference_profile_required_string_payload(value))
