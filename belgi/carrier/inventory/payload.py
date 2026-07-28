"""Carrier inventory JSON payload types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from belgi.carrier.exceptions import MemberError
from belgi.substrate.io import canonical_json_text, parse_json_value

JsonScalar: TypeAlias = None | bool | int | float | str
JsonCompatible: TypeAlias = (
    JsonScalar | list["JsonCompatible"] | dict[str, "JsonCompatible"]
)

__all__ = [
    "JsonCompatible",
    "JsonPayload",
    "JsonScalar",
]


def _inventory_payload_canonical_json_bytes(*, value: JsonCompatible) -> bytes:
    try:
        return canonical_json_text(value).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise MemberError("Value cannot be represented as deterministic JSON.") from exc


def _inventory_payload_json_compatible_value(
    *,
    value: object,
    label: str,
) -> JsonCompatible:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        return [
            _inventory_payload_json_compatible_value(value=item, label=f"{label}[]")
            for item in value
        ]
    if isinstance(value, dict):
        converted: dict[str, JsonCompatible] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise MemberError(f"{label} must use string object keys.")
            converted[key] = _inventory_payload_json_compatible_value(
                value=item,
                label=f"{label}.{key}",
            )
        return converted
    raise MemberError(f"{label} must contain only JSON-compatible values.")


def _inventory_payload_json_from_canonical_bytes(*, value: bytes) -> JsonCompatible:
    try:
        decoded = parse_json_value(value, label="stored JSON payload")
    except ValueError as exc:
        raise MemberError("Stored JSON payload is not valid UTF-8 JSON.") from exc
    return _inventory_payload_json_compatible_value(
        value=decoded,
        label="stored JSON payload",
    )


@dataclass(frozen=True, slots=True, kw_only=True)
class JsonPayload:
    """Deterministic JSON payload used for inline declaration content."""

    canonical_bytes: bytes

    def __post_init__(self) -> None:
        _inventory_payload_json_from_canonical_bytes(value=self.canonical_bytes)

    @classmethod
    def from_value(cls, *, value: JsonCompatible) -> JsonPayload:
        return cls(canonical_bytes=_inventory_payload_canonical_json_bytes(value=value))

    @classmethod
    def from_json_bytes(cls, *, json_bytes: bytes) -> JsonPayload:
        return cls(
            canonical_bytes=_inventory_payload_canonical_json_bytes(
                value=_inventory_payload_json_from_canonical_bytes(value=json_bytes),
            )
        )

    def to_compatible_value(self) -> JsonCompatible:
        return _inventory_payload_json_from_canonical_bytes(value=self.canonical_bytes)
