from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier import (
    ClaimRecord,
    DependencyKind,
    EvidenceStateCarrier,
    MemberInventoryEntry,
    ReferencedSourceKind,
)
from belgi.core import EvidenceState
from belgi.profile.edition import EditionKind
from belgi.profile.reference_profile.evidence import (
    EvidenceKindOwnershipRegistry,
    reference_profile_evidence_state_from_carrier_items,
)
from belgi.replay.carriers import parse_evidence_state_carrier
from belgi.replay.lifting.model import (
    LiftedCarrier,
    ParsedCarrier,
    ResolvedCarrier,
    ResolvedDependencies,
)
from belgi.replay.parsing import dependency_references_for_member_names
from belgi.replay.reference_profile.source_authority import (
    Part4RootAuthority,
    carrier_designator,
    exact_part4_carrier_designator,
    part4_root_authority,
    require_resolved_source_authority,
    resolved_source_designators,
    root_references_part4_source,
)

from .resolution import (
    ResolvedReferenceProfileEvidenceStateCarrier,
    resolve_reference_profile_evidence_state_carrier,
)

__all__ = ["EvidenceStateReferenceProfileAdapter"]


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceStateReferenceProfileAdapter:
    ownership_registry: EvidenceKindOwnershipRegistry

    def parse(
        self,
        *,
        root_member: MemberInventoryEntry,
        root_bytes: bytes,
        claim_record: ClaimRecord,
    ) -> ParsedCarrier[EvidenceStateCarrier]:
        carrier = parse_evidence_state_carrier(
            root_bytes=root_bytes,
            description="evidence-state carrier",
            claim_record=claim_record,
        )
        owners = self.ownership_registry.declared_owners(
            evidence_kind_identifiers=tuple(
                str(item.evidence_kind_identifier) for item in carrier.evidence_items
            )
        )
        exact_designators = [
            carrier_designator(designator=owner.immutable_designator)
            for owner in owners
        ]
        if root_references_part4_source(
            claim_record=claim_record,
            root_member=root_member,
        ):
            exact_designators.append(exact_part4_carrier_designator())
        return ParsedCarrier(
            root_member=root_member,
            root_bytes=root_bytes,
            parsed_carrier=carrier,
            dependency_references=dependency_references_for_member_names(
                member_names=carrier.referenced_member_names(),
                claim_record=claim_record,
            ),
            exact_edition_designators=tuple(dict.fromkeys(exact_designators)),
        )

    def resolve(
        self,
        *,
        parsed: ParsedCarrier[EvidenceStateCarrier],
        dependencies: ResolvedDependencies,
        claim_record: ClaimRecord,
    ) -> ResolvedCarrier[ResolvedReferenceProfileEvidenceStateCarrier]:
        owners = self.ownership_registry.declared_owners(
            evidence_kind_identifiers=tuple(
                str(item.evidence_kind_identifier)
                for item in parsed.parsed_carrier.evidence_items
            )
        )
        for owner in owners:
            require_resolved_source_authority(
                resolved=dependencies,
                claim_record=claim_record,
                root_member=parsed.root_member,
                designator=carrier_designator(designator=owner.immutable_designator),
                allowed_roles=_owner_source_roles(owner_kind=owner.kind),
            )
        authority = part4_root_authority(
            claim_record=claim_record,
            root_member=parsed.root_member,
        )
        if authority is Part4RootAuthority.DETERMINING_SEMANTICS:
            require_resolved_source_authority(
                resolved=dependencies,
                claim_record=claim_record,
                root_member=parsed.root_member,
                designator=exact_part4_carrier_designator(),
                allowed_roles=(
                    (
                        ReferencedSourceKind.DETERMINING_SEMANTICS,
                        DependencyKind.DETERMINING_SEMANTICS,
                    ),
                ),
            )
        return ResolvedCarrier(
            root_member=parsed.root_member,
            resolved_carrier=resolve_reference_profile_evidence_state_carrier(
                carrier=parsed.parsed_carrier,
                dependencies=dependencies,
                claim_record=claim_record,
            ),
            dependencies=dependencies,
        )

    def induce(
        self,
        *,
        resolved: ResolvedCarrier[ResolvedReferenceProfileEvidenceStateCarrier],
        claim_record: ClaimRecord,
    ) -> LiftedCarrier[EvidenceState]:
        resolved_designators = resolved_source_designators(
            resolved=resolved.dependencies
        )
        return LiftedCarrier(
            root_member=resolved.root_member,
            semantic_object=reference_profile_evidence_state_from_carrier_items(
                carrier_items=resolved.resolved_carrier.evidence_items,
                resolved_owner_designators=resolved_designators,
                ownership_registry=self.ownership_registry,
            ),
        )


def _owner_source_roles(
    *, owner_kind: EditionKind
) -> tuple[tuple[ReferencedSourceKind, DependencyKind], ...]:
    if owner_kind is EditionKind.PROFILE:
        return (
            (ReferencedSourceKind.PROFILE, DependencyKind.PROFILE_MATERIAL),
            (
                ReferencedSourceKind.DETERMINING_SEMANTICS,
                DependencyKind.DETERMINING_SEMANTICS,
            ),
        )
    if owner_kind is EditionKind.COMPANION:
        return ((ReferencedSourceKind.COMPANION, DependencyKind.COMPANION_MATERIAL),)
    return ((ReferencedSourceKind.OTHER, DependencyKind.OTHER),)
