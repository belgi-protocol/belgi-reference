from __future__ import annotations

import math
from collections.abc import Hashable, Mapping


def freeze_json_compatible_value(value: object) -> Hashable:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("JSON-compatible numbers must be finite.")
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        return tuple(freeze_json_compatible_value(item) for item in value)
    if isinstance(value, Mapping):
        frozen_items: list[tuple[str, Hashable]] = []
        for key, item in sorted(value.items(), key=lambda entry: entry[0]):
            if not isinstance(key, str):
                raise ValueError("JSON-compatible mappings must use string keys.")
            frozen_items.append((key, freeze_json_compatible_value(item)))
        return tuple(frozen_items)
    raise ValueError("Value must be JSON-compatible to be frozen canonically.")


__all__ = ["freeze_json_compatible_value"]
