from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier.inventory import (
    carrier_schema_release,
)
from belgi.substrate.io import decode_strict_json


@dataclass(frozen=True, slots=True, kw_only=True)
class SchemaInventoryEntry:
    schema_name: str
    uri: str
    sha256: str
    role: str
    dependencies: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class CarrierSchemaInventory:
    schema_id_base: str
    dialect_uri: str
    entries_by_name: dict[str, SchemaInventoryEntry]


def _require_schema_inventory_text(
    *, document: dict[str, object], field: str, label: str
) -> str:
    value = document.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label}.{field} must be a non-empty string")
    return value


def parse_carrier_schema_inventory(raw: bytes) -> CarrierSchemaInventory:
    value = decode_strict_json(raw, maximum_depth=128)
    if not isinstance(value, dict):
        raise ValueError("carrier schema inventory must be a JSON object")
    if value.get("schemaVersion") != "belgi-json-representation-schema-inventory-v2":
        raise ValueError("unsupported carrier schema inventory version")
    schema_id_base = _require_schema_inventory_text(
        document=value,
        field="schemaIdBase",
        label="carrier schema inventory",
    )
    dialect_uri = _require_schema_inventory_text(
        document=value,
        field="dialectUri",
        label="carrier schema inventory",
    )
    carrier_schema_release(
        schema_id_base=schema_id_base,
        dialect_uri=dialect_uri,
    )
    raw_entries = value.get("entries")
    if not isinstance(raw_entries, list):
        raise ValueError("carrier schema inventory entries must be an array")
    entries: dict[str, SchemaInventoryEntry] = {}
    for index, raw_entry in enumerate(raw_entries):
        if not isinstance(raw_entry, dict):
            raise ValueError(
                f"carrier schema inventory entries[{index}] must be an object"
            )
        label = f"carrier schema inventory entries[{index}]"
        schema_name = _require_schema_inventory_text(
            document=raw_entry,
            field="schemaName",
            label=label,
        )
        if schema_name in entries:
            raise ValueError(f"duplicate carrier schema inventory entry: {schema_name}")
        dependencies = raw_entry.get("dependencies")
        if not isinstance(dependencies, list) or not all(
            isinstance(item, str) and item for item in dependencies
        ):
            raise ValueError(f"{label}.dependencies must be an array of names")
        if len(set(dependencies)) != len(dependencies):
            raise ValueError(f"{label}.dependencies must be unique")
        entries[schema_name] = SchemaInventoryEntry(
            schema_name=schema_name,
            uri=_require_schema_inventory_text(
                document=raw_entry, field="uri", label=label
            ),
            sha256=_require_schema_inventory_text(
                document=raw_entry, field="sha256", label=label
            ),
            role=_require_schema_inventory_text(
                document=raw_entry, field="role", label=label
            ),
            dependencies=tuple(dependencies),
        )
    return CarrierSchemaInventory(
        schema_id_base=schema_id_base,
        dialect_uri=dialect_uri,
        entries_by_name=entries,
    )


__all__ = [
    "CarrierSchemaInventory",
    "SchemaInventoryEntry",
    "parse_carrier_schema_inventory",
]
