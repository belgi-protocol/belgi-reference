from __future__ import annotations

import json
import math
from collections.abc import Mapping
from typing import NoReturn


def _reject_non_finite_json_number(value: str) -> NoReturn:
    raise ValueError(f"non-finite JSON number {value!r} is not permitted")


def _require_finite_json_numbers(value: object) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite JSON number is not permitted")
    if isinstance(value, list):
        for item in value:
            _require_finite_json_numbers(item)
        return
    if isinstance(value, Mapping):
        for item in value.values():
            _require_finite_json_numbers(item)


class _DuplicateTrackingJSONObject(dict[str, object]):
    __slots__ = ("duplicate_keys",)

    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        duplicates: list[str] = []
        seen: set[str] = set()
        for key, value in pairs:
            if key in seen:
                duplicates.append(key)
                continue
            seen.add(key)
            self[key] = value
        self.duplicate_keys = tuple(dict.fromkeys(duplicates))


def _require_unique_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    document = _DuplicateTrackingJSONObject(pairs)
    if document.duplicate_keys:
        raise ValueError(
            "duplicate JSON object keys are not permitted: "
            + ", ".join(document.duplicate_keys)
        )
    return dict(document)


def parse_json_value(raw: str | bytes, *, label: str) -> object:
    try:
        text = raw.decode("utf-8", errors="strict") if isinstance(raw, bytes) else raw
        obj = json.loads(
            text,
            object_pairs_hook=_require_unique_json_object,
            parse_constant=_reject_non_finite_json_number,
        )
        _require_finite_json_numbers(obj)
        return obj
    except RecursionError as error:
        raise ValueError(
            f"{label} is not valid UTF-8 JSON: maximum nesting depth exceeded"
        ) from error
    except (UnicodeDecodeError, ValueError) as error:
        raise ValueError(f"{label} is not valid UTF-8 JSON: {error}") from error


def parse_json_object(raw: str | bytes, *, label: str) -> dict[str, object]:
    obj = parse_json_value(raw, label=label)
    if not isinstance(obj, dict):
        raise ValueError(f"{label} must be a JSON object")
    return obj


def parse_json_object_with_duplicate_tracking(
    raw: str | bytes,
    *,
    label: str,
) -> _DuplicateTrackingJSONObject:
    try:
        text = raw.decode("utf-8", errors="strict") if isinstance(raw, bytes) else raw
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} is not valid UTF-8 JSON") from error
    try:
        obj = json.loads(
            text,
            object_pairs_hook=_DuplicateTrackingJSONObject,
            parse_constant=_reject_non_finite_json_number,
        )
        _require_finite_json_numbers(obj)
    except RecursionError as error:
        raise ValueError(
            f"{label} is not valid UTF-8 JSON: maximum nesting depth exceeded"
        ) from error
    except ValueError as error:
        raise ValueError(f"{label} is not valid UTF-8 JSON: {error}") from error
    if not isinstance(obj, _DuplicateTrackingJSONObject):
        raise ValueError(f"{label} must be a JSON object")
    return obj


def _duplicate_json_keys(obj: Mapping[str, object]) -> tuple[str, ...]:
    duplicates: list[str] = []

    def _collect(value: object) -> None:
        if isinstance(value, _DuplicateTrackingJSONObject):
            duplicates.extend(value.duplicate_keys)
            for child in value.values():
                _collect(child)
            return
        if isinstance(value, list):
            for child in value:
                _collect(child)

    _collect(obj)
    return tuple(dict.fromkeys(duplicates))


def require_no_duplicate_json_keys(
    *,
    obj: Mapping[str, object],
    label: str,
) -> None:
    duplicates = _duplicate_json_keys(obj)
    if duplicates:
        raise ValueError(f"{label} contains duplicate keys: {', '.join(duplicates)}")


__all__ = [
    "parse_json_object",
    "parse_json_object_with_duplicate_tracking",
    "parse_json_value",
    "require_no_duplicate_json_keys",
]
