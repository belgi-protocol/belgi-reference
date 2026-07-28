from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.exceptions import ReferenceProfileReplayError
from belgi.profile.reference_profile.identifiers import ALL_ENVIRONMENT_TERMS

__all__ = [
    "reference_profile_optional_environment_terms",
    "reference_profile_optional_equivalence_basis",
    "reference_profile_optional_json_bool",
    "reference_profile_optional_json_int",
    "reference_profile_optional_json_int_or_bool",
    "reference_profile_optional_json_number",
]


def reference_profile_optional_json_bool(
    *,
    obj: Mapping[str, object],
    key: str,
    description: str,
) -> bool | None:
    value = obj.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ReferenceProfileReplayError(
            f"{description} subject_field '{key}' must be absent or a bool",
        )
    return value


def reference_profile_optional_json_int(
    *,
    obj: Mapping[str, object],
    key: str,
    description: str,
) -> int | None:
    value = obj.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ReferenceProfileReplayError(
            f"{description} subject_field '{key}' must be absent or an int",
        )
    return value


def reference_profile_optional_json_int_or_bool(
    *,
    obj: Mapping[str, object],
    key: str,
    description: str,
) -> int | bool | None:
    value = obj.get(key)
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    raise ReferenceProfileReplayError(
        f"{description} subject_field '{key}' must be absent or an int/bool",
    )


def reference_profile_optional_json_number(
    *,
    obj: Mapping[str, object],
    key: str,
    description: str,
) -> float | None:
    value = obj.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReferenceProfileReplayError(
            f"{description} subject_field '{key}' must be absent or a number",
        )
    return float(value)


def reference_profile_optional_environment_terms(
    *,
    source_content: Mapping[str, object],
) -> dict[str, object] | None:
    environment_terms: dict[str, object] = {}
    for field_name in ("environment_terms", "environment"):
        value = source_content.get(field_name)
        if not isinstance(value, Mapping):
            continue
        for key, item in value.items():
            environment_terms[str(key)] = item
    for term_id in ALL_ENVIRONMENT_TERMS:
        canonical_name = str(term_id)
        alias_name = canonical_name.split(".")[-1].replace("-", "_")
        if canonical_name in source_content:
            environment_terms[canonical_name] = source_content[canonical_name]
            continue
        if alias_name in source_content:
            environment_terms[canonical_name] = source_content[alias_name]
    if not environment_terms:
        return None
    return environment_terms


def reference_profile_optional_equivalence_basis(
    *,
    source_content: Mapping[str, object],
) -> str | None:
    for field_name in ("equivalence_basis", "equivalence", "environment_equivalence"):
        value = source_content.get(field_name)
        if value is not None:
            return str(value)
    return None
