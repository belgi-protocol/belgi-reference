"""Carrier package member inventory public seam."""

from __future__ import annotations

from belgi.carrier.exceptions import (
    CarrierError,
    DuplicateMemberNameError,
    InvalidContentLocatorError,
    InvalidDeclarationParameterError,
    InvalidDigestError,
    InvalidInventoryEntryError,
    InvalidMemberDraftError,
    InvalidMemberNameError,
    InvalidRepresentationBindingError,
    MemberError,
)

from .designators import (
    SCHEMA_ID_BASE,
    Digest,
    ImmutableDesignator,
    carrier_schema_designator,
    carrier_schema_digests,
)
from .identity import (
    CanonicalReference,
    MemberName,
    PackageIdentifier,
    ParameterIdentifier,
    ReferenceResolver,
    carrier_schema_release,
    require_carrier_schema_resource_uri,
    require_package_identifier,
)
from .membership import (
    MemberClassification,
    MemberDraft,
    MemberInventory,
    MemberInventoryEntry,
    MemberRole,
    PackageMember,
    classify_member_role,
    dedupe_member_names,
)
from .payload import JsonCompatible, JsonPayload, JsonScalar
from .representation import (
    ContentLocator,
    ContentLocatorMode,
    DeclarationParameter,
    RepresentationBinding,
)

__all__ = [
    "SCHEMA_ID_BASE",
    "CanonicalReference",
    "CarrierError",
    "ContentLocator",
    "ContentLocatorMode",
    "DeclarationParameter",
    "Digest",
    "DuplicateMemberNameError",
    "ImmutableDesignator",
    "InvalidContentLocatorError",
    "InvalidDeclarationParameterError",
    "InvalidDigestError",
    "InvalidInventoryEntryError",
    "InvalidMemberDraftError",
    "InvalidMemberNameError",
    "InvalidRepresentationBindingError",
    "JsonCompatible",
    "JsonPayload",
    "JsonScalar",
    "MemberClassification",
    "MemberDraft",
    "MemberError",
    "MemberInventory",
    "MemberInventoryEntry",
    "MemberName",
    "MemberRole",
    "PackageIdentifier",
    "PackageMember",
    "ParameterIdentifier",
    "ReferenceResolver",
    "RepresentationBinding",
    "carrier_schema_designator",
    "carrier_schema_digests",
    "carrier_schema_release",
    "classify_member_role",
    "dedupe_member_names",
    "require_carrier_schema_resource_uri",
    "require_package_identifier",
]
