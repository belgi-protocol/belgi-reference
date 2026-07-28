"""Carrier inventory identity types."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import NewType

from belgi.substrate.io.path_syntax import (
    is_portable_path_segment,
    is_uri_unreserved_segment,
)

PackageIdentifier = NewType("PackageIdentifier", str)
MemberName = NewType("MemberName", str)
CanonicalReference = NewType("CanonicalReference", str)
ParameterIdentifier = NewType("ParameterIdentifier", str)

ReferenceResolver = Callable[[MemberName], CanonicalReference]

_DIALECT_FILENAME = "BELGI-JSON-Schema-Dialect.schema.json"
_SCHEMA_ID_BASE = re.compile(
    r"https://belgi\.dev/schemas/carrier/(?P<release>rc\.v[1-9][0-9]*)"
)


def carrier_schema_release(*, schema_id_base: str, dialect_uri: str) -> str:
    """Validate one carrier release identity and return its release designator."""

    match = _SCHEMA_ID_BASE.fullmatch(schema_id_base)
    if match is None:
        raise ValueError(
            "schema inventory schemaIdBase must match "
            "'https://belgi.dev/schemas/carrier/rc.vN' with N >= 1."
        )
    expected_dialect_uri = f"{schema_id_base}/{_DIALECT_FILENAME}"
    if dialect_uri != expected_dialect_uri:
        raise ValueError(
            "schema inventory dialectUri must select the declared carrier release "
            f"dialect: {expected_dialect_uri!r}."
        )
    return match.group("release")


def require_carrier_schema_resource_uri(*, uri: str, filename: str) -> str:
    """Require one schema resource URI under a canonical carrier release base."""

    if not (
        filename.endswith(".schema.json")
        and is_uri_unreserved_segment(filename)
        and is_portable_path_segment(filename)
    ):
        raise ValueError("carrier schema filename is not canonical.")
    suffix = f"/{filename}"
    if not uri.endswith(suffix):
        raise ValueError("carrier schema URI does not select its source filename.")
    schema_id_base = uri[: -len(suffix)]
    return carrier_schema_release(
        schema_id_base=schema_id_base,
        dialect_uri=f"{schema_id_base}/{_DIALECT_FILENAME}",
    )


def require_package_identifier(
    *,
    value: object,
    label: str,
    error_type: type[Exception],
) -> PackageIdentifier:
    """Preserve one exact non-empty JSON string as a package identifier."""

    if not isinstance(value, str) or value == "":
        raise error_type(f"{label} must be a non-empty string.")
    return PackageIdentifier(value)


__all__ = [
    "CanonicalReference",
    "MemberName",
    "PackageIdentifier",
    "ParameterIdentifier",
    "ReferenceResolver",
    "carrier_schema_release",
    "require_carrier_schema_resource_uri",
    "require_package_identifier",
]
