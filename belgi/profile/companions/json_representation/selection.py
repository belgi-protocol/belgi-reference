"""Exact JSON-companion selection for physical package procedures."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.edition import ExactEditionBinding, ImmutableDesignator
from belgi.substrate.hash import sha256_bytes

from .edition import COMPANION_IDENTIFIER, COMPANION_VERSION

__all__ = [
    "DIRECTORY_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER",
    "JSON_REPRESENTATION_COMPANION_IDENTIFIER",
    "JSON_REPRESENTATION_COMPANION_VERSION",
    "ZIP_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER",
    "PackageRepresentationSelection",
    "select_package_representation",
]

JSON_REPRESENTATION_COMPANION_IDENTIFIER = str(COMPANION_IDENTIFIER)
JSON_REPRESENTATION_COMPANION_VERSION = str(COMPANION_VERSION)
DIRECTORY_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER = (
    "https://belgi.dev/ids/procedure/replay-package/directory-v1"
)
ZIP_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER = (
    "https://belgi.dev/ids/procedure/replay-package/zip-v1"
)
_SUPPORTED_PROCEDURE_IDENTIFIERS = frozenset(
    {
        DIRECTORY_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER,
        ZIP_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER,
    }
)


@dataclass(frozen=True, slots=True, kw_only=True)
class PackageRepresentationSelection:
    """Profile-owned selection; outer composition converts it for carriers."""

    procedure_identifier: str
    defining_source: ImmutableDesignator


def select_package_representation(
    *,
    procedure_identifier: str,
    companion_binding: ExactEditionBinding,
    supported_companion_binding: ExactEditionBinding,
    companion_source_bytes: bytes,
) -> PackageRepresentationSelection:
    """Select one procedure only through an exact companion binding and bytes."""

    if procedure_identifier not in _SUPPORTED_PROCEDURE_IDENTIFIERS:
        raise ValueError(
            f"unsupported package-representation procedure: {procedure_identifier!r}"
        )
    if (
        companion_binding.kind.value != "companion"
        or str(companion_binding.family_identifier)
        != JSON_REPRESENTATION_COMPANION_IDENTIFIER
        or str(companion_binding.version_designator)
        != JSON_REPRESENTATION_COMPANION_VERSION
    ):
        raise ValueError(
            "selected package representation requires the exact active "
            "spec-0.5 JSON representation companion binding"
        )
    if companion_binding != supported_companion_binding:
        raise ValueError(
            "selected JSON representation companion binding does not match "
            "the supported exact edition"
        )
    designator = companion_binding.immutable_designator
    if designator.digest.algorithm_id != "sha256":
        raise ValueError(
            "JSON representation companion designator must use the exact "
            "sha256 algorithm token"
        )
    if sha256_bytes(companion_source_bytes) != designator.digest.digest_value:
        raise ValueError(
            "JSON representation companion designator does not bind the "
            "selected exact source bytes"
        )
    return PackageRepresentationSelection(
        procedure_identifier=procedure_identifier,
        defining_source=designator,
    )
