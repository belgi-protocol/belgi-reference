"""Claim-record public surface."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal, TypeAlias

from belgi.carrier.exceptions import (
    ClaimRecordError,
    DependencyDeclarationError,
    RootDesignationError,
)
from belgi.carrier.integrity import canonical_json_document_bytes
from belgi.carrier.inventory import (
    CanonicalReference,
    ImmutableDesignator,
    JsonCompatible,
    MemberInventory,
    MemberName,
    PackageIdentifier,
    RepresentationBinding,
    carrier_schema_designator,
)

from .serialize import claim_record_to_json_object
from .validate import validate_claim_record

__all__ = [
    "CLAIM_RECORD_MEDIA_TYPE",
    "CLAIM_RECORD_SCHEMA_DESIGNATOR",
    "CachedVerdict",
    "ClaimRecord",
    "DependencyDeclaration",
    "DependencyKind",
    "ReferencedSourceBinding",
    "ReferencedSourceKind",
    "RootDesignators",
]


CLAIM_RECORD_MEDIA_TYPE = "application/vnd.belgi.claim-record+json"
CLAIM_RECORD_SCHEMA_DESIGNATOR = carrier_schema_designator(
    schema_name="ClaimRecord.schema.json"
)
CachedVerdict: TypeAlias = Literal[0, 1]


class DependencyKind(str, Enum):
    """Replay-relevant dependency category preserved in the claim record."""

    JUDGED_OBJECT_INPUT = "judged-object-input"
    EVIDENCE_INPUT = "evidence-input"
    EVALUATOR_INPUT = "evaluator-input"
    PROFILE_MATERIAL = "profile-material"
    COMPANION_MATERIAL = "companion-material"
    GOVERNING_SPECIFICATION = "governing-specification"
    DETERMINING_SEMANTICS = "determining-semantics"
    OTHER = "other"


class ReferencedSourceKind(str, Enum):
    """Replay-relevant external source category preserved in the claim record."""

    PROFILE = "profile"
    COMPANION = "companion"
    GOVERNING_SPECIFICATION = "governing-specification"
    DETERMINING_SEMANTICS = "determining-semantics"
    OTHER = "other"


@dataclass(frozen=True, slots=True, kw_only=True)
class RootDesignators:
    """Required root designators for the three semantic carrier sorts."""

    judged_object_carrier_reference: CanonicalReference
    evidence_state_carrier_reference: CanonicalReference
    evaluator_carrier_reference: CanonicalReference

    def __post_init__(self) -> None:
        seen = {
            self.judged_object_carrier_reference,
            self.evidence_state_carrier_reference,
            self.evaluator_carrier_reference,
        }
        if len(seen) != 3:
            raise RootDesignationError(
                "Each required root designator shall designate a different member."
            )

    @classmethod
    def from_preserved_read(
        cls,
        *,
        judged_object_carrier_reference: CanonicalReference,
        evidence_state_carrier_reference: CanonicalReference,
        evaluator_carrier_reference: CanonicalReference,
    ) -> RootDesignators:
        instance = object.__new__(cls)
        object.__setattr__(
            instance,
            "judged_object_carrier_reference",
            judged_object_carrier_reference,
        )
        object.__setattr__(
            instance,
            "evidence_state_carrier_reference",
            evidence_state_carrier_reference,
        )
        object.__setattr__(
            instance,
            "evaluator_carrier_reference",
            evaluator_carrier_reference,
        )
        return instance

    def to_json_object(self) -> dict[str, JsonCompatible]:
        return {
            "judgedObjectCarrier": str(self.judged_object_carrier_reference),
            "evidenceStateCarrier": str(self.evidence_state_carrier_reference),
            "evaluatorCarrier": str(self.evaluator_carrier_reference),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class DependencyDeclaration:
    """Replay-relevant member dependency preserved in the claim record."""

    dependent_reference: CanonicalReference
    dependency_reference: CanonicalReference
    dependency_kind: DependencyKind

    def __post_init__(self) -> None:
        if self.dependent_reference == self.dependency_reference:
            raise DependencyDeclarationError(
                "Replay-relevant dependencies shall not self-reference."
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferencedSourceBinding:
    """Binding from an immutable external designator to a replay-relevant member."""

    source_kind: ReferencedSourceKind
    designator: ImmutableDesignator
    member_reference: CanonicalReference


@dataclass(frozen=True, slots=True, kw_only=True)
class ClaimRecord:
    """Preserved claim record for one replay package."""

    package_identifier: PackageIdentifier
    root_designators: RootDesignators
    member_inventory: MemberInventory
    dependency_declarations: tuple[DependencyDeclaration, ...]
    referenced_sources: tuple[ReferencedSourceBinding, ...]
    package_integrity_manifest_member_name: MemberName
    package_integrity_anchor_member_name: MemberName
    notes: tuple[str, ...] = ()
    cached_verdict: CachedVerdict | None = None

    def __post_init__(self) -> None:
        if str(self.package_identifier) == "":
            raise ClaimRecordError("package_identifier must be non-empty.")
        if self.cached_verdict is not None and self.cached_verdict not in (0, 1):
            raise ClaimRecordError("cached_verdict must be 0, 1, or absent.")
        validate_claim_record(claim_record=self)

    @classmethod
    def from_preserved_read(
        cls,
        *,
        package_identifier: PackageIdentifier,
        root_designators: RootDesignators,
        member_inventory: MemberInventory,
        dependency_declarations: tuple[DependencyDeclaration, ...],
        referenced_sources: tuple[ReferencedSourceBinding, ...],
        package_integrity_manifest_member_name: MemberName,
        package_integrity_anchor_member_name: MemberName,
        notes: tuple[str, ...] = (),
        cached_verdict: CachedVerdict | None = None,
    ) -> ClaimRecord:
        if str(package_identifier) == "":
            raise ClaimRecordError("package_identifier must be non-empty.")
        if cached_verdict is not None and cached_verdict not in (0, 1):
            raise ClaimRecordError("cached_verdict must be 0, 1, or absent.")
        instance = object.__new__(cls)
        object.__setattr__(instance, "package_identifier", package_identifier)
        object.__setattr__(instance, "root_designators", root_designators)
        object.__setattr__(instance, "member_inventory", member_inventory)
        object.__setattr__(
            instance,
            "dependency_declarations",
            dependency_declarations,
        )
        object.__setattr__(instance, "referenced_sources", referenced_sources)
        object.__setattr__(
            instance,
            "package_integrity_manifest_member_name",
            package_integrity_manifest_member_name,
        )
        object.__setattr__(
            instance,
            "package_integrity_anchor_member_name",
            package_integrity_anchor_member_name,
        )
        object.__setattr__(instance, "notes", notes)
        object.__setattr__(instance, "cached_verdict", cached_verdict)
        return instance

    @property
    def representation(self) -> RepresentationBinding:
        return RepresentationBinding(
            media_type=CLAIM_RECORD_MEDIA_TYPE,
            schema_designator=CLAIM_RECORD_SCHEMA_DESIGNATOR,
        )

    def to_json_object(self) -> dict[str, JsonCompatible]:
        return claim_record_to_json_object(claim_record=self)

    def to_json_bytes(self) -> bytes:
        return canonical_json_document_bytes(document=self.to_json_object())
