"""Carrier package membership and inventory types."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from belgi.carrier.exceptions import (
    DuplicateMemberNameError,
    InvalidInventoryEntryError,
    InvalidMemberDraftError,
    InvalidMemberNameError,
    MemberError,
)

from .designators import ImmutableDesignator
from .identity import CanonicalReference, MemberName
from .representation import RepresentationBinding

if TYPE_CHECKING:
    from belgi.carrier.projection import ProjectionResult, ProjectionSpec

__all__ = [
    "MemberClassification",
    "MemberDraft",
    "MemberInventory",
    "MemberInventoryEntry",
    "MemberRole",
    "PackageMember",
    "classify_member_role",
    "dedupe_member_names",
]


def _inventory_membership_required_text(*, value: str, label: str) -> None:
    if value.strip() == "":
        raise InvalidMemberNameError(f"{label} must be non-empty.")


def dedupe_member_names(
    *,
    member_names: tuple[MemberName, ...],
) -> tuple[MemberName, ...]:
    seen: set[MemberName] = set()
    ordered: list[MemberName] = []
    for member_name in member_names:
        if member_name in seen:
            continue
        seen.add(member_name)
        ordered.append(member_name)
    return tuple(ordered)


class MemberClassification(str, Enum):
    """Claim-record classification of a package member."""

    REPLAY_RELEVANT = "replay-relevant"
    CLAIM_RECORD_INTEGRITY_RECOVERY = "claim-record-integrity-recovery"
    AUXILIARY = "auxiliary"


class MemberRole(str, Enum):
    """Carrier-layer role of a package member."""

    CLAIM_RECORD = "claim-record"
    PACKAGE_INTEGRITY_MANIFEST = "package-integrity-manifest"
    PACKAGE_INTEGRITY_ANCHOR = "package-integrity-anchor"
    JUDGED_OBJECT_CARRIER_ROOT = "judged-object-carrier-root"
    EVIDENCE_STATE_CARRIER_ROOT = "evidence-state-carrier-root"
    EVALUATOR_CARRIER_ROOT = "evaluator-carrier-root"
    REPLAY_DEPENDENCY = "replay-dependency"
    AUXILIARY = "auxiliary"


def classify_member_role(*, member_role: MemberRole) -> MemberClassification:
    if member_role in {
        MemberRole.PACKAGE_INTEGRITY_MANIFEST,
        MemberRole.PACKAGE_INTEGRITY_ANCHOR,
    }:
        return MemberClassification.CLAIM_RECORD_INTEGRITY_RECOVERY
    if member_role is MemberRole.AUXILIARY:
        return MemberClassification.AUXILIARY
    return MemberClassification.REPLAY_RELEVANT


@dataclass(frozen=True, slots=True, kw_only=True)
class MemberDraft:
    """Producer-side package member before canonical reference assignment."""

    member_name: MemberName
    member_role: MemberRole
    representation: RepresentationBinding
    preserved_bytes: bytes
    classification: MemberClassification
    projection_spec: ProjectionSpec | None = None

    def __post_init__(self) -> None:
        _inventory_membership_required_text(
            value=str(self.member_name),
            label="member_name",
        )
        expected_classification = classify_member_role(member_role=self.member_role)
        if self.classification is not expected_classification:
            raise InvalidMemberDraftError("member_role and classification must agree.")
        if (
            self.classification is not MemberClassification.REPLAY_RELEVANT
            and self.projection_spec is not None
        ):
            raise InvalidMemberDraftError(
                "Non-replay-relevant members shall not declare replay-relevant "
                "projections."
            )

    @classmethod
    def replay_relevant(
        cls,
        *,
        member_name: MemberName,
        member_role: MemberRole,
        representation: RepresentationBinding,
        preserved_bytes: bytes,
        projection_spec: ProjectionSpec | None = None,
    ) -> MemberDraft:
        if (
            classify_member_role(member_role=member_role)
            is not MemberClassification.REPLAY_RELEVANT
        ):
            raise InvalidMemberDraftError(
                "Only replay-relevant member roles may use "
                "MemberDraft.replay_relevant()."
            )
        return cls(
            member_name=member_name,
            member_role=member_role,
            representation=representation,
            preserved_bytes=preserved_bytes,
            classification=MemberClassification.REPLAY_RELEVANT,
            projection_spec=projection_spec,
        )

    @classmethod
    def auxiliary(
        cls,
        *,
        member_name: MemberName,
        representation: RepresentationBinding,
        preserved_bytes: bytes,
    ) -> MemberDraft:
        return cls(
            member_name=member_name,
            member_role=MemberRole.AUXILIARY,
            representation=representation,
            preserved_bytes=preserved_bytes,
            classification=MemberClassification.AUXILIARY,
            projection_spec=None,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class PackageMember:
    """Final package member with canonical-reference and projection metadata."""

    member_name: MemberName
    member_role: MemberRole
    representation: RepresentationBinding
    preserved_bytes: bytes
    classification: MemberClassification
    canonical_reference: CanonicalReference | None
    projection: ProjectionResult | None

    def __post_init__(self) -> None:
        _inventory_membership_required_text(
            value=str(self.member_name),
            label="member_name",
        )
        expected_classification = classify_member_role(member_role=self.member_role)
        if self.classification is not expected_classification:
            raise InvalidInventoryEntryError(
                "member_role and classification must agree."
            )
        if self.classification is MemberClassification.REPLAY_RELEVANT:
            if self.canonical_reference is None or self.projection is None:
                raise InvalidInventoryEntryError(
                    "Replay-relevant members require a canonical reference and a "
                    "replay-relevant projection."
                )
            return
        if self.canonical_reference is not None or self.projection is not None:
            raise InvalidInventoryEntryError(
                "Non-replay-relevant members shall not carry canonical references "
                "or projections."
            )

    def as_inventory_entry(self) -> MemberInventoryEntry:
        projection_rule_identifier = None
        projection_rule_designator = None
        if self.projection is not None:
            projection_rule_identifier = self.projection.projection_rule_identifier
            projection_rule_designator = self.projection.projection_rule_designator
        return MemberInventoryEntry(
            member_name=self.member_name,
            member_role=self.member_role,
            classification=self.classification,
            representation=self.representation,
            canonical_reference=self.canonical_reference,
            projection_rule_identifier=projection_rule_identifier,
            projection_rule_designator=projection_rule_designator,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class MemberInventoryEntry:
    """Claim-record inventory row for one package member."""

    member_name: MemberName
    member_role: MemberRole
    classification: MemberClassification
    representation: RepresentationBinding
    canonical_reference: CanonicalReference | None
    projection_rule_identifier: str | None = None
    projection_rule_designator: ImmutableDesignator | None = None

    def __post_init__(self) -> None:
        _inventory_membership_required_text(
            value=str(self.member_name),
            label="member_name",
        )
        expected_classification = classify_member_role(member_role=self.member_role)
        if self.classification is not expected_classification:
            raise InvalidInventoryEntryError(
                "member_role and classification must agree."
            )
        if self.classification is MemberClassification.REPLAY_RELEVANT:
            if self.canonical_reference is None:
                raise InvalidInventoryEntryError(
                    "Replay-relevant inventory entries require canonical references."
                )
            if (self.projection_rule_identifier is None) != (
                self.projection_rule_designator is None
            ):
                raise InvalidInventoryEntryError(
                    "Projection-rule identifier and designator must be paired."
                )
            if self.projection_rule_identifier is not None:
                _inventory_membership_required_text(
                    value=self.projection_rule_identifier,
                    label="projection_rule_identifier",
                )
            return
        if (
            self.canonical_reference is not None
            or self.projection_rule_identifier is not None
            or self.projection_rule_designator is not None
        ):
            raise InvalidInventoryEntryError(
                "Non-replay-relevant inventory entries shall not carry "
                "replay-relevant metadata."
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class MemberInventory:
    """Complete member inventory preserved inside a claim record."""

    entries: tuple[MemberInventoryEntry, ...]

    def __post_init__(self) -> None:
        if len(self.entries) == 0:
            raise InvalidInventoryEntryError(
                "Member inventory must contain at least one entry."
            )
        seen_names: set[MemberName] = set()
        seen_references: set[CanonicalReference] = set()
        for entry in self.entries:
            if entry.member_name in seen_names:
                raise DuplicateMemberNameError(
                    f"Duplicate member name in inventory: {entry.member_name}"
                )
            seen_names.add(entry.member_name)
            if entry.canonical_reference is None:
                continue
            if entry.canonical_reference in seen_references:
                raise InvalidInventoryEntryError(
                    "Duplicate canonical reference in inventory: "
                    f"{entry.canonical_reference}"
                )
            seen_references.add(entry.canonical_reference)

    @classmethod
    def from_preserved_read(
        cls,
        *,
        entries: tuple[MemberInventoryEntry, ...],
    ) -> MemberInventory:
        if len(entries) == 0:
            raise InvalidInventoryEntryError(
                "Member inventory must contain at least one entry."
            )
        seen_names: set[MemberName] = set()
        for entry in entries:
            if entry.member_name in seen_names:
                raise DuplicateMemberNameError(
                    f"Duplicate member name in inventory: {entry.member_name}"
                )
            seen_names.add(entry.member_name)
        instance = object.__new__(cls)
        object.__setattr__(instance, "entries", entries)
        return instance

    def entry_for_name(self, *, member_name: MemberName) -> MemberInventoryEntry:
        for entry in self.entries:
            if entry.member_name == member_name:
                return entry
        raise MemberError(f"Unknown member name: {member_name}")

    def entry_for_reference(
        self,
        *,
        canonical_reference: CanonicalReference,
    ) -> MemberInventoryEntry:
        for entry in self.entries:
            if entry.canonical_reference == canonical_reference:
                return entry
        raise MemberError(f"Unknown canonical reference: {canonical_reference}")

    def replay_relevant_entries(self) -> tuple[MemberInventoryEntry, ...]:
        return tuple(
            entry
            for entry in self.entries
            if entry.classification is MemberClassification.REPLAY_RELEVANT
        )

    def auxiliary_entries(self) -> tuple[MemberInventoryEntry, ...]:
        return tuple(
            entry
            for entry in self.entries
            if entry.classification is MemberClassification.AUXILIARY
        )

    def claim_record_integrity_recovery_entries(
        self,
    ) -> tuple[MemberInventoryEntry, ...]:
        return tuple(
            entry
            for entry in self.entries
            if (
                entry.classification
                is MemberClassification.CLAIM_RECORD_INTEGRITY_RECOVERY
            )
        )

    def canonical_references(self) -> tuple[CanonicalReference, ...]:
        return tuple(
            entry.canonical_reference
            for entry in self.replay_relevant_entries()
            if entry.canonical_reference is not None
        )
