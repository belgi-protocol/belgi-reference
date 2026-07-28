from __future__ import annotations

from typing import Any

from belgi.substrate.schema.types import json_type_name


def _is_json_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def json_values_equal(left: Any, right: Any) -> bool:
    if _is_json_number(left) and _is_json_number(right):
        return bool(left == right)
    if json_type_name(left) != json_type_name(right):
        return False
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            json_values_equal(left_item, right_item)
            for left_item, right_item in zip(left, right, strict=True)
        )
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            json_values_equal(left[key], right[key]) for key in left
        )
    return bool(left == right)
