from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from types import MappingProxyType
from urllib.parse import urlparse

from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from belgi.substrate.schema.exceptions import SchemaGraphError


def _require_absolute_uri(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise SchemaGraphError(f"{field} must be a non-empty absolute URI")
    parsed = urlparse(value)
    if not parsed.scheme or parsed.fragment:
        raise SchemaGraphError(f"{field} must be an absolute URI without a fragment")
    return value


@dataclass(frozen=True, slots=True)
class LocalSchemaRegistry:
    """An immutable, no-retrieval Draft 2020-12 schema resource set."""

    dialect_uri: str
    schemas_by_uri: Mapping[str, dict[str, object]]

    @classmethod
    def from_documents(
        cls,
        *,
        dialect_uri: str,
        documents: Sequence[dict[str, object]],
    ) -> LocalSchemaRegistry:
        required_dialect_uri = _require_absolute_uri(
            dialect_uri,
            field="dialect_uri",
        )
        schemas: dict[str, dict[str, object]] = {}
        for index, document in enumerate(documents):
            uri = _require_absolute_uri(
                document.get("$id"),
                field=f"documents[{index}].$id",
            )
            if uri in schemas:
                raise SchemaGraphError(f"duplicate schema resource URI: {uri}")
            schemas[uri] = deepcopy(document)
        if required_dialect_uri not in schemas:
            raise SchemaGraphError(
                f"dialect resource is absent from local schema graph: {required_dialect_uri}"
            )
        return cls(
            dialect_uri=required_dialect_uri,
            schemas_by_uri=MappingProxyType(schemas),
        )

    def without_uris(self, unavailable_uris: Iterable[str]) -> LocalSchemaRegistry:
        unavailable = frozenset(unavailable_uris)
        retained = [
            schema
            for uri, schema in self.schemas_by_uri.items()
            if uri not in unavailable
        ]
        if self.dialect_uri in unavailable:
            raise SchemaGraphError("the local dialect resource cannot be removed")
        return LocalSchemaRegistry.from_documents(
            dialect_uri=self.dialect_uri,
            documents=retained,
        )

    def referencing_registry(self) -> Registry[dict[str, object]]:
        resources = (
            (uri, Resource(contents=schema, specification=DRAFT202012))
            for uri, schema in self.schemas_by_uri.items()
        )
        return Registry().with_resources(resources)
