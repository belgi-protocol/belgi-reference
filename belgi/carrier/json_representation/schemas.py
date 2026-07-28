from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from belgi.carrier.inventory import SCHEMA_ID_BASE
from belgi.substrate.hash import sha256_bytes
from belgi.substrate.io import decode_strict_json
from belgi.substrate.resource import load_packaged_bytes
from belgi.substrate.schema.exceptions import SchemaGraphError
from belgi.substrate.schema.model import SchemaIssue
from belgi.substrate.schema.reference import LocalSchemaRegistry
from belgi.substrate.schema.walker import validate_local_schema

from .graph_authority import (
    require_declared_schema_dependencies,
    trusted_schema_uris_by_role,
)
from .inventory import CarrierSchemaInventory, parse_carrier_schema_inventory
from .roles import TrustedJSONRole

_SCHEMA_BASE_URI = f"{SCHEMA_ID_BASE}/"
_DIALECT_URI = _SCHEMA_BASE_URI + "BELGI-JSON-Schema-Dialect.schema.json"


def _parse_inventory(inventory_bytes: bytes) -> CarrierSchemaInventory:
    try:
        return parse_carrier_schema_inventory(inventory_bytes)
    except ValueError as exc:
        raise SchemaGraphError("carrier schema inventory is malformed") from exc


def _authenticated_schema_documents(
    *,
    inventory: CarrierSchemaInventory,
    schema_bytes_by_name: Mapping[str, bytes],
) -> dict[str, dict[str, object]]:
    schema_names = frozenset(inventory.entries_by_name)
    observed_names = frozenset(schema_bytes_by_name)
    if observed_names != schema_names:
        raise SchemaGraphError(
            "carrier schema byte set mismatch: "
            f"missing={sorted(schema_names - observed_names)}, "
            f"extra={sorted(observed_names - schema_names)}"
        )
    documents: dict[str, dict[str, object]] = {}
    for name, raw in schema_bytes_by_name.items():
        entry = inventory.entries_by_name[name]
        expected_uri = _SCHEMA_BASE_URI + name
        if entry.uri != expected_uri:
            raise SchemaGraphError(f"carrier schema inventory URI mismatch for {name}")
        observed_sha256 = sha256_bytes(raw)
        if observed_sha256 != entry.sha256:
            raise SchemaGraphError(
                f"carrier schema byte digest mismatch for {name}: "
                f"expected {entry.sha256}, observed {observed_sha256}"
            )
        try:
            value = decode_strict_json(raw, maximum_depth=128)
        except ValueError as exc:
            raise SchemaGraphError(f"carrier schema {name} is not strict JSON") from exc
        if not isinstance(value, dict):
            raise SchemaGraphError(f"carrier schema {name} must be a JSON object")
        if value.get("$id") != expected_uri:
            raise SchemaGraphError(
                f"carrier schema identifier mismatch for {name}: "
                f"expected {expected_uri!r}"
            )
        documents[name] = value
    require_declared_schema_dependencies(
        inventory=inventory,
        documents_by_name=documents,
    )
    return documents


@dataclass(frozen=True, slots=True)
class CarrierSchemaGraph:
    """The exact local carrier schema resources used after trusted-role selection."""

    registry: LocalSchemaRegistry
    _schema_uri_by_trusted_role: Mapping[TrustedJSONRole, str]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "_schema_uri_by_trusted_role",
            MappingProxyType(dict(self._schema_uri_by_trusted_role)),
        )

    @classmethod
    def from_inventory_bytes(
        cls,
        *,
        inventory_bytes: bytes,
        schema_bytes_by_name: Mapping[str, bytes],
        unavailable_schema_names: Iterable[str] = (),
    ) -> CarrierSchemaGraph:
        inventory = _parse_inventory(inventory_bytes)
        return cls._from_inventory(
            inventory=inventory,
            schema_bytes_by_name=schema_bytes_by_name,
            unavailable_schema_names=unavailable_schema_names,
        )

    @classmethod
    def _from_inventory(
        cls,
        *,
        inventory: CarrierSchemaInventory,
        schema_bytes_by_name: Mapping[str, bytes],
        unavailable_schema_names: Iterable[str],
    ) -> CarrierSchemaGraph:
        schema_uri_by_trusted_role = trusted_schema_uris_by_role(inventory)
        if inventory.schema_id_base != SCHEMA_ID_BASE:
            raise SchemaGraphError("carrier schema inventory ID base mismatch")
        if inventory.dialect_uri != _DIALECT_URI:
            raise SchemaGraphError("carrier schema inventory dialect URI mismatch")
        schema_names = frozenset(inventory.entries_by_name)
        unavailable = frozenset(unavailable_schema_names)
        unknown_unavailable = unavailable - schema_names
        if unknown_unavailable:
            raise SchemaGraphError(
                "unknown unavailable carrier schema names: "
                + ", ".join(sorted(unknown_unavailable))
            )
        dialect_name = next(
            entry.schema_name
            for entry in inventory.entries_by_name.values()
            if entry.role == "dialect"
        )
        if dialect_name in unavailable:
            raise SchemaGraphError("the carrier schema dialect cannot be unavailable")
        documents = _authenticated_schema_documents(
            inventory=inventory,
            schema_bytes_by_name=schema_bytes_by_name,
        )
        registry = LocalSchemaRegistry.from_documents(
            dialect_uri=_DIALECT_URI,
            documents=tuple(documents.values()),
        )
        if unavailable:
            registry = registry.without_uris(
                inventory.entries_by_name[name].uri for name in unavailable
            )
        return cls(
            registry=registry,
            _schema_uri_by_trusted_role=schema_uri_by_trusted_role,
        )

    @classmethod
    def from_package(
        cls,
        *,
        unavailable_schema_names: Iterable[str] = (),
    ) -> CarrierSchemaGraph:
        unavailable = frozenset(unavailable_schema_names)
        try:
            inventory_bytes = load_packaged_bytes(
                package_name="belgi.carrier",
                path_parts=("schema-inventory.json",),
                label="carrier schema inventory",
            )
            inventory = _parse_inventory(inventory_bytes)
            trusted_schema_uris_by_role(inventory)
            schema_bytes = {
                name: load_packaged_bytes(
                    package_name="belgi.carrier",
                    path_parts=("schemas", name),
                    label=f"carrier schema {name}",
                )
                for name in sorted(inventory.entries_by_name)
            }
        except SchemaGraphError:
            raise
        except ValueError as exc:
            raise SchemaGraphError(
                "could not load packaged carrier schema graph resources"
            ) from exc
        return cls._from_inventory(
            inventory=inventory,
            schema_bytes_by_name=schema_bytes,
            unavailable_schema_names=unavailable,
        )

    def validate(
        self,
        *,
        instance: object,
        trusted_role: TrustedJSONRole,
        path: str,
    ) -> list[SchemaIssue]:
        return validate_local_schema(
            registry=self.registry,
            instance=instance,
            root_uri=self._schema_uri_by_trusted_role[trusted_role],
            path=path,
        )


__all__ = ["CarrierSchemaGraph"]
