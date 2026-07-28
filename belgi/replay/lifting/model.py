from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from belgi.carrier import (
    CanonicalReference,
    ClaimRecord,
    ImmutableDesignator,
    MemberInventoryEntry,
    PackageMember,
    ReferencedSourceBinding,
)

from .exceptions import LiftingStage
from .source_binding import VerifiedReferencedSource

__all__ = [
    "CarrierLiftingAdapter",
    "InduceRecord",
    "LiftedCarrier",
    "LiftingTrace",
    "ParseRecord",
    "ParsedCarrier",
    "ResolveRecord",
    "ResolvedCarrier",
    "ResolvedDependencies",
    "ResolvedPackageMember",
    "ResolvedReferencedSource",
]

ParsedT = TypeVar("ParsedT")
ResolvedT = TypeVar("ResolvedT")
SemanticT = TypeVar("SemanticT")


@dataclass(frozen=True, slots=True, kw_only=True)
class ParseRecord(Generic[ParsedT]):
    stage: LiftingStage
    root_reference: CanonicalReference
    value: ParsedT


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolveRecord(Generic[ResolvedT]):
    stage: LiftingStage
    root_reference: CanonicalReference
    value: ResolvedT


@dataclass(frozen=True, slots=True, kw_only=True)
class InduceRecord(Generic[SemanticT]):
    stage: LiftingStage
    root_reference: CanonicalReference
    value: SemanticT


@dataclass(frozen=True, slots=True, kw_only=True)
class LiftingTrace(Generic[ParsedT, ResolvedT, SemanticT]):
    parsed: ParseRecord[ParsedT]
    resolved: ResolveRecord[ResolvedT]
    induced: InduceRecord[SemanticT]


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolvedPackageMember:
    inventory_entry: MemberInventoryEntry
    package_member: PackageMember

    @property
    def canonical_reference(self) -> CanonicalReference:
        reference = self.inventory_entry.canonical_reference
        if reference is None:
            raise ValueError(
                "Resolved replay-relevant members must carry canonical references."
            )
        return reference

    @property
    def preserved_bytes(self) -> bytes:
        return self.package_member.preserved_bytes


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolvedReferencedSource:
    member: ResolvedPackageMember
    binding: ReferencedSourceBinding
    verified_source: VerifiedReferencedSource


@dataclass(frozen=True, slots=True, kw_only=True)
class ParsedCarrier(Generic[ParsedT]):
    root_member: MemberInventoryEntry
    root_bytes: bytes
    parsed_carrier: ParsedT
    dependency_references: tuple[CanonicalReference, ...]
    exact_edition_designators: tuple[ImmutableDesignator, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolvedDependencies:
    member_dependencies: tuple[ResolvedPackageMember, ...]
    referenced_sources: tuple[ResolvedReferencedSource, ...]

    def member_for_reference(
        self, *, canonical_reference: CanonicalReference
    ) -> ResolvedPackageMember | None:
        for dependency in self.member_dependencies:
            if dependency.canonical_reference == canonical_reference:
                return dependency
        return None

    def referenced_source_for_designator(
        self, *, designator: ImmutableDesignator
    ) -> ResolvedReferencedSource | None:
        for source in self.referenced_sources:
            if source.binding.designator == designator:
                return source
        return None


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolvedCarrier(Generic[ResolvedT]):
    root_member: MemberInventoryEntry
    resolved_carrier: ResolvedT
    dependencies: ResolvedDependencies


@dataclass(frozen=True, slots=True, kw_only=True)
class LiftedCarrier(Generic[SemanticT]):
    root_member: MemberInventoryEntry
    semantic_object: SemanticT


class CarrierLiftingAdapter(Protocol[ParsedT, ResolvedT, SemanticT]):
    def parse(
        self,
        *,
        root_member: MemberInventoryEntry,
        root_bytes: bytes,
        claim_record: ClaimRecord,
    ) -> ParsedCarrier[ParsedT]: ...

    def resolve(
        self,
        *,
        parsed: ParsedCarrier[ParsedT],
        dependencies: ResolvedDependencies,
        claim_record: ClaimRecord,
    ) -> ResolvedCarrier[ResolvedT]: ...

    def induce(
        self,
        *,
        resolved: ResolvedCarrier[ResolvedT],
        claim_record: ClaimRecord,
    ) -> LiftedCarrier[SemanticT]: ...
