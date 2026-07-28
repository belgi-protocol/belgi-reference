from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileEvidenceStateCompileError,
)

__all__ = [
    "reference_profile_evidence_optional_bool",
    "reference_profile_evidence_optional_int",
    "reference_profile_evidence_optional_int_or_bool",
    "reference_profile_evidence_optional_mapping",
    "reference_profile_evidence_optional_number",
    "reference_profile_evidence_optional_text",
    "reference_profile_evidence_required_text",
]


def reference_profile_evidence_required_text(
    *,
    document: Mapping[str, object],
    key: str,
    semantic_slice: str,
    detail_prefix: str,
) -> str:
    value = document.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice=semantic_slice,
            detail=f"{detail_prefix} must be a non-empty string.",
        )
    return value


def reference_profile_evidence_optional_text(
    *,
    document: Mapping[str, object],
    key: str,
    semantic_slice: str,
    detail_prefix: str,
) -> str | None:
    value = document.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice=semantic_slice,
            detail=f"{detail_prefix} must be a non-empty string when present.",
        )
    return value


def reference_profile_evidence_optional_bool(
    *,
    document: Mapping[str, object],
    key: str,
    semantic_slice: str,
    detail_prefix: str,
) -> bool | None:
    value = document.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice=semantic_slice,
            detail=f"{detail_prefix} must be a bool when present.",
        )
    return value


def reference_profile_evidence_optional_int(
    *,
    document: Mapping[str, object],
    key: str,
    semantic_slice: str,
    detail_prefix: str,
) -> int | None:
    value = document.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice=semantic_slice,
            detail=f"{detail_prefix} must be an int when present.",
        )
    return value


def reference_profile_evidence_optional_int_or_bool(
    *,
    document: Mapping[str, object],
    key: str,
    semantic_slice: str,
    detail_prefix: str,
) -> int | bool | None:
    value = document.get(key)
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    raise ReferenceProfileEvidenceStateCompileError(
        semantic_slice=semantic_slice,
        detail=f"{detail_prefix} must be an int or bool when present.",
    )


def reference_profile_evidence_optional_number(
    *,
    document: Mapping[str, object],
    key: str,
    semantic_slice: str,
    detail_prefix: str,
) -> float | None:
    value = document.get(key)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice=semantic_slice,
            detail=f"{detail_prefix} must be a number when present.",
        )
    return float(value)


def reference_profile_evidence_optional_mapping(
    *,
    document: Mapping[str, object],
    key: str,
    semantic_slice: str,
    detail_prefix: str,
) -> dict[str, object] | None:
    value = document.get(key)
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ReferenceProfileEvidenceStateCompileError(
            semantic_slice=semantic_slice,
            detail=f"{detail_prefix} must be an object when present.",
        )
    return dict(value.items())
