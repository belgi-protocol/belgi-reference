"""Bounded pre-authentication view of claim-record recovery fields."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from belgi.carrier.exceptions import ClaimRecordError
from belgi.carrier.inventory import (
    MemberName,
    PackageIdentifier,
    require_package_identifier,
)
from belgi.carrier.json_representation import validate_json_representation

_CLAIM_RECORD_MEMBER_NAME = "claim-record"


@dataclass(frozen=True, slots=True, kw_only=True)
class ClaimRecordBootstrapEntry:
    """Minimal immutable raw fields selected during bounded bootstrap."""

    member_name: MemberName
    canonical_reference_payload: object | None
    member_role_payload: object | None
    classification_payload: object | None
    media_type_payload: object | None
    schema_designator_payload: object | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ClaimRecordBootstrap:
    preserved_claim_record_bytes: bytes
    package_identifier: PackageIdentifier
    package_integrity_manifest_member_name: MemberName
    package_integrity_anchor_member_name: MemberName
    member_entries: tuple[ClaimRecordBootstrapEntry, ...]

    @property
    def claim_record_entry(self) -> ClaimRecordBootstrapEntry:
        return self.entry_for_name(member_name=MemberName(_CLAIM_RECORD_MEMBER_NAME))

    @property
    def manifest_entry(self) -> ClaimRecordBootstrapEntry:
        return self.entry_for_name(
            member_name=self.package_integrity_manifest_member_name
        )

    @property
    def anchor_entry(self) -> ClaimRecordBootstrapEntry:
        return self.entry_for_name(
            member_name=self.package_integrity_anchor_member_name
        )

    def entry_for_name(self, *, member_name: MemberName) -> ClaimRecordBootstrapEntry:
        for entry in self.member_entries:
            if entry.member_name == member_name:
                return entry
        return ClaimRecordBootstrapEntry(
            member_name=member_name,
            canonical_reference_payload=None,
            member_role_payload=None,
            classification_payload=None,
            media_type_payload=None,
            schema_designator_payload=None,
        )


def _freeze_json_value(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType(
            {key: _freeze_json_value(item) for key, item in value.items()}
        )
    if isinstance(value, list):
        return tuple(_freeze_json_value(item) for item in value)
    return value


def _bootstrap_entry(*, member_name: str, payload: object) -> ClaimRecordBootstrapEntry:
    entry = payload if isinstance(payload, Mapping) else {}
    representation_payload = entry.get("representation")
    representation = (
        representation_payload if isinstance(representation_payload, Mapping) else {}
    )
    return ClaimRecordBootstrapEntry(
        member_name=MemberName(member_name),
        canonical_reference_payload=_freeze_json_value(entry.get("canonicalReference")),
        member_role_payload=_freeze_json_value(entry.get("memberRole")),
        classification_payload=_freeze_json_value(entry.get("classification")),
        media_type_payload=_freeze_json_value(representation.get("mediaType")),
        schema_designator_payload=_freeze_json_value(
            representation.get("schemaDesignator")
        ),
    )


def _require_bootstrap_member_name(*, value: object, label: str) -> MemberName:
    """Preserve one exact non-empty member designation during Step 1."""

    if not isinstance(value, str) or value == "":
        raise ClaimRecordError(f"{label} must be a non-empty string.")
    return MemberName(value)


def parse_claim_record_bootstrap(
    *,
    claim_record_bytes: bytes,
    maximum_member_count: int,
    maximum_member_name_octets: int,
) -> ClaimRecordBootstrap:
    """Read only fields needed to authenticate the exact claim-record octets."""

    outcome = validate_json_representation(claim_record_bytes)
    if not outcome.accepted or not isinstance(outcome.value, dict):
        raise ClaimRecordError(
            "claim record bootstrap representation rejected at "
            f"{outcome.stage}: {outcome.result_code}."
        )
    payload = outcome.value
    if payload.get("kind") != "claim-record":
        raise ClaimRecordError("claim record bootstrap kind is invalid.")
    inventory = payload.get("memberInventory")
    if not isinstance(inventory, dict):
        raise ClaimRecordError(
            "claim record bootstrap memberInventory must be an object."
        )
    if len(inventory) > maximum_member_count:
        raise ClaimRecordError(
            "claim record bootstrap memberInventory exceeds its member envelope."
        )
    for member_name in inventory:
        if len(member_name.encode("utf-8")) > maximum_member_name_octets:
            raise ClaimRecordError(
                "claim record bootstrap member name exceeds its byte envelope."
            )
    manifest_name = _require_bootstrap_member_name(
        value=payload.get("packageIntegrityManifestMember"),
        label="claim record bootstrap.packageIntegrityManifestMember",
    )
    anchor_name = _require_bootstrap_member_name(
        value=payload.get("packageIntegrityAnchorMember"),
        label="claim record bootstrap.packageIntegrityAnchorMember",
    )
    return ClaimRecordBootstrap(
        preserved_claim_record_bytes=bytes(claim_record_bytes),
        package_identifier=require_package_identifier(
            value=payload.get("packageIdentifier"),
            label="claim record bootstrap.packageIdentifier",
            error_type=ClaimRecordError,
        ),
        package_integrity_manifest_member_name=manifest_name,
        package_integrity_anchor_member_name=anchor_name,
        member_entries=tuple(
            _bootstrap_entry(member_name=member_name, payload=inventory[member_name])
            for member_name in sorted(
                inventory,
                key=lambda name: name.encode("utf-8"),
            )
        ),
    )


__all__ = [
    "ClaimRecordBootstrap",
    "ClaimRecordBootstrapEntry",
    "parse_claim_record_bootstrap",
]
