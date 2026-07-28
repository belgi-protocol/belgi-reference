from __future__ import annotations

import base64
from dataclasses import dataclass

from belgi.carrier import (
    CanonicalReference,
    Digest,
    ImmutableDesignator,
    MemberClassification,
    MemberInventoryEntry,
    MemberName,
    MemberRole,
    PackageIdentifier,
    PackageMember,
    RepresentationBinding,
    compute_projection,
)
from belgi.carrier.inventory import require_package_identifier
from belgi.substrate.schema.api import require_schema_object

from .exceptions import PackageSourceMemberNotFoundError
from .protocol import ReplayPackageSource

__all__ = [
    "EmbeddedReplayPackageSource",
    "load_embedded_replay_package_members",
    "load_embedded_replay_package_source",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class EmbeddedReplayPackageSource(ReplayPackageSource):
    package_identifier: PackageIdentifier
    members: tuple[PackageMember, ...]

    def __post_init__(self) -> None:
        require_package_identifier(
            value=self.package_identifier,
            label="embedded replay package source.package_identifier",
            error_type=ValueError,
        )
        object.__setattr__(self, "members", tuple(self.members))
        member_names = tuple(member.member_name for member in self.members)
        if len(member_names) != len(set(member_names)):
            raise ValueError("embedded replay package source has duplicate members.")
        claim_record_members = tuple(
            member
            for member in self.members
            if member.member_role is MemberRole.CLAIM_RECORD
        )
        if len(claim_record_members) != 1:
            raise ValueError(
                "embedded replay package source requires exactly one claim-record member."
            )

    def claim_record_bytes(self) -> bytes:
        return self._claim_record_member().preserved_bytes

    def has_bootstrap_member(self, *, member_name: MemberName) -> bool:
        try:
            self._member_by_name(member_name=member_name)
        except PackageSourceMemberNotFoundError:
            return False
        return True

    def read_bootstrap_member(self, *, member_name: MemberName) -> bytes:
        return self._member_by_name(member_name=member_name).preserved_bytes

    def has_member(self, *, inventory_entry: MemberInventoryEntry) -> bool:
        try:
            return (
                self._member_by_name(
                    member_name=inventory_entry.member_name
                ).as_inventory_entry()
                == inventory_entry
            )
        except PackageSourceMemberNotFoundError:
            return False

    def read_member(self, *, inventory_entry: MemberInventoryEntry) -> bytes:
        return self.package_member(inventory_entry=inventory_entry).preserved_bytes

    def package_member(self, *, inventory_entry: MemberInventoryEntry) -> PackageMember:
        member = self._member_by_name(member_name=inventory_entry.member_name)
        if member.as_inventory_entry() != inventory_entry:
            raise ValueError(
                "Embedded replay package member does not match the supplied inventory entry."
            )
        return member

    def _claim_record_member(self) -> PackageMember:
        for member in self.members:
            if member.member_role is MemberRole.CLAIM_RECORD:
                return member
        raise ValueError("embedded replay package claim-record member is missing.")

    def _member_by_name(self, *, member_name: MemberName) -> PackageMember:
        for member in self.members:
            if member.member_name == member_name:
                return member
        raise PackageSourceMemberNotFoundError(
            f"embedded replay package member is missing: {member_name}"
        )


def load_embedded_replay_package_source(
    *,
    payload: object,
    label: str,
) -> EmbeddedReplayPackageSource:
    package_payload = require_schema_object(payload, label=label)
    return EmbeddedReplayPackageSource(
        package_identifier=PackageIdentifier(
            _embedded_replay_package_text(
                payload=package_payload,
                field_name="packageIdentifier",
            )
        ),
        members=load_embedded_replay_package_members(
            payload=package_payload,
            label=label,
        ),
    )


def load_embedded_replay_package_members(
    *,
    payload: object,
    label: str,
) -> tuple[PackageMember, ...]:
    package_payload = require_schema_object(payload, label=label)
    members_payload = package_payload.get("members")
    if not isinstance(members_payload, list) or not members_payload:
        raise ValueError(f"{label}.members must be a non-empty array.")
    return tuple(
        _embedded_replay_package_member(
            payload=require_schema_object(member, label=f"{label}.member")
        )
        for member in members_payload
    )


def _embedded_replay_package_member(
    *,
    payload: dict[str, object],
) -> PackageMember:
    representation = require_schema_object(
        payload.get("representation"),
        label="embedded replay package member.representation",
    )
    classification = MemberClassification(
        _embedded_replay_package_text(
            payload=payload,
            field_name="classification",
        )
    )
    preserved_bytes_base64 = payload.get("preservedBytesBase64")
    if not isinstance(preserved_bytes_base64, str):
        raise ValueError("preservedBytesBase64 must be a string.")
    preserved_bytes = base64.b64decode(preserved_bytes_base64, validate=True)
    projection = (
        compute_projection(preserved_bytes=preserved_bytes, projection_spec=None)
        if classification is MemberClassification.REPLAY_RELEVANT
        else None
    )
    canonical_reference = payload.get("canonicalReference")
    return PackageMember(
        member_name=MemberName(
            _embedded_replay_package_text(
                payload=payload,
                field_name="memberName",
            )
        ),
        member_role=MemberRole(
            _embedded_replay_package_text(
                payload=payload,
                field_name="memberRole",
            )
        ),
        representation=RepresentationBinding(
            media_type=_embedded_replay_package_text(
                payload=representation,
                field_name="mediaType",
            ),
            schema_designator=_embedded_replay_package_optional_designator(
                payload=representation.get("schemaDesignator"),
                label="embedded replay package member.schemaDesignator",
            ),
        ),
        preserved_bytes=preserved_bytes,
        classification=classification,
        canonical_reference=(
            None
            if canonical_reference is None
            else CanonicalReference(str(canonical_reference))
        ),
        projection=projection,
    )


def _embedded_replay_package_optional_designator(
    *,
    payload: object | None,
    label: str,
) -> ImmutableDesignator | None:
    if payload is None:
        return None
    return _embedded_replay_package_payload_designator(payload=payload, label=label)


def _embedded_replay_package_payload_designator(
    *,
    payload: object,
    label: str,
) -> ImmutableDesignator:
    designator = require_schema_object(payload, label=label)
    digest = require_schema_object(designator.get("digest"), label=f"{label}.digest")
    return ImmutableDesignator(
        uri=_embedded_replay_package_text(
            payload=designator,
            field_name="uri",
        ),
        digest=Digest(
            algorithm_id=_embedded_replay_package_text(
                payload=digest,
                field_name="algorithmId",
            ),
            digest_value=_embedded_replay_package_text(
                payload=digest,
                field_name="digestValue",
            ),
        ),
    )


def _embedded_replay_package_text(
    *,
    payload: dict[str, object],
    field_name: str,
) -> str:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value
