from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import PurePosixPath, PureWindowsPath
from types import MappingProxyType
from urllib.parse import urldefrag, urljoin

from belgi.substrate.schema.exceptions import SchemaGraphError

from .inventory import CarrierSchemaInventory, SchemaInventoryEntry
from .roles import TrustedJSONRole

_DEPENDENCY_SCHEMA_ROLES = frozenset(
    {"dialect", "common-definitions", "failure-taxonomy"}
)
_JSON_SCHEMA_META_URI_PREFIX = "https://json-schema.org/draft/2020-12/"
_PORTABLE_SCHEMA_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.schema\.json\Z")
_WINDOWS_RESERVED_DEVICE_STEMS = frozenset(
    {"aux", "con", "nul", "prn"}
    | {f"com{number}" for number in range(1, 10)}
    | {f"lpt{number}" for number in range(1, 10)}
)


def _require_safe_inventory_entries(
    inventory: CarrierSchemaInventory,
) -> Mapping[str, str]:
    schema_name_by_role: dict[str, str] = {}
    schema_name_by_uri: dict[str, str] = {}
    schema_names = frozenset(inventory.entries_by_name)
    for schema_name, entry in inventory.entries_by_name.items():
        windows_path = PureWindowsPath(schema_name)
        device_stem = schema_name.partition(".")[0].casefold()
        if not (
            PurePosixPath(schema_name).name == schema_name
            and windows_path.name == schema_name
            and not windows_path.drive
            and not any(character in schema_name for character in ("\\", ":", "\x00"))
            and _PORTABLE_SCHEMA_NAME.fullmatch(schema_name) is not None
            and device_stem not in _WINDOWS_RESERVED_DEVICE_STEMS
        ):
            raise SchemaGraphError(
                f"carrier schema inventory has unsafe schema name: {schema_name!r}"
            )
        if entry.role in schema_name_by_role:
            raise SchemaGraphError(
                f"carrier schema inventory has duplicate role: {entry.role!r}"
            )
        if entry.uri in schema_name_by_uri:
            raise SchemaGraphError(
                f"carrier schema inventory has duplicate URI: {entry.uri!r}"
            )
        unknown_dependencies = frozenset(entry.dependencies) - schema_names
        if unknown_dependencies:
            raise SchemaGraphError(
                f"carrier schema inventory has unknown dependencies for {schema_name}: "
                + ", ".join(sorted(unknown_dependencies))
            )
        schema_name_by_role[entry.role] = schema_name
        schema_name_by_uri[entry.uri] = schema_name

    expected_roles = frozenset(role.value for role in TrustedJSONRole).union(
        _DEPENDENCY_SCHEMA_ROLES
    )
    observed_roles = frozenset(schema_name_by_role)
    if observed_roles != expected_roles:
        raise SchemaGraphError(
            "carrier schema inventory role set mismatch: "
            f"missing={sorted(expected_roles - observed_roles)}, "
            f"extra={sorted(observed_roles - expected_roles)}"
        )
    dialect_name = schema_name_by_role["dialect"]
    if inventory.entries_by_name[dialect_name].uri != inventory.dialect_uri:
        raise SchemaGraphError(
            "carrier schema inventory dialect role does not bind dialectUri"
        )
    return schema_name_by_role


def trusted_schema_uris_by_role(
    inventory: CarrierSchemaInventory,
) -> Mapping[TrustedJSONRole, str]:
    """Derive the immutable instance-root selector from one parsed inventory."""

    schema_name_by_role = _require_safe_inventory_entries(inventory)
    return MappingProxyType(
        {
            role: inventory.entries_by_name[schema_name_by_role[role.value]].uri
            for role in TrustedJSONRole
        }
    )


def _referenced_schema_names(
    *,
    document: dict[str, object],
    source_entry: SchemaInventoryEntry,
    entries_by_uri: Mapping[str, SchemaInventoryEntry],
) -> frozenset[str]:
    referenced_names: set[str] = set()

    def visit(value: object, *, base_uri: str) -> None:
        if isinstance(value, list):
            for child in value:
                visit(child, base_uri=base_uri)
            return
        if not isinstance(value, dict):
            return

        identifier = value.get("$id")
        local_base_uri = (
            urljoin(base_uri, identifier) if isinstance(identifier, str) else base_uri
        )
        for keyword in ("$ref", "$dynamicRef"):
            reference = value.get(keyword)
            if not isinstance(reference, str):
                continue
            target_uri, _fragment = urldefrag(urljoin(local_base_uri, reference))
            if target_uri.startswith(_JSON_SCHEMA_META_URI_PREFIX):
                continue
            target_entry = entries_by_uri.get(target_uri)
            if target_entry is None:
                raise SchemaGraphError(
                    f"carrier schema {source_entry.schema_name} has unresolved "
                    f"non-meta {keyword}: {reference!r}"
                )
            if target_entry.schema_name != source_entry.schema_name:
                referenced_names.add(target_entry.schema_name)
        for child in value.values():
            visit(child, base_uri=local_base_uri)

    visit(document, base_uri=source_entry.uri)
    return frozenset(referenced_names)


def require_declared_schema_dependencies(
    *,
    inventory: CarrierSchemaInventory,
    documents_by_name: Mapping[str, dict[str, object]],
) -> None:
    """Authenticate inventory dependency sets against the loaded local ref graph."""

    entries_by_uri = {entry.uri: entry for entry in inventory.entries_by_name.values()}
    for schema_name, entry in inventory.entries_by_name.items():
        observed_dependencies = _referenced_schema_names(
            document=documents_by_name[schema_name],
            source_entry=entry,
            entries_by_uri=entries_by_uri,
        )
        declared_dependencies = frozenset(entry.dependencies)
        if declared_dependencies != observed_dependencies:
            raise SchemaGraphError(
                f"carrier schema inventory dependencies differ for {schema_name}: "
                f"expected={sorted(observed_dependencies)}, "
                f"observed={sorted(declared_dependencies)}"
            )


__all__ = [
    "require_declared_schema_dependencies",
    "trusted_schema_uris_by_role",
]
