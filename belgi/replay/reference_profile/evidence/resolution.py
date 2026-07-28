from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier import (
    ClaimRecord,
    ContentLocatorMode,
    EvidenceItem,
    EvidenceStateCarrier,
)
from belgi.carrier.json_representation import validate_json_representation
from belgi.replay.lifting.exceptions import ResolveFailureError
from belgi.replay.lifting.model import ResolvedDependencies

from .model import ReferenceProfileEvidenceCarrierItem

__all__ = ["ResolvedReferenceProfileEvidenceStateCarrier"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolvedReferenceProfileEvidenceStateCarrier:
    evidence_items: tuple[ReferenceProfileEvidenceCarrierItem, ...]


def resolve_reference_profile_evidence_state_carrier(
    *,
    carrier: EvidenceStateCarrier,
    dependencies: ResolvedDependencies,
    claim_record: ClaimRecord,
) -> ResolvedReferenceProfileEvidenceStateCarrier:
    return ResolvedReferenceProfileEvidenceStateCarrier(
        evidence_items=tuple(
            _resolved_reference_profile_evidence_item(
                evidence_item=evidence_item,
                dependencies=dependencies,
                claim_record=claim_record,
            )
            for evidence_item in carrier.evidence_items
        )
    )


def _resolved_reference_profile_evidence_item(
    *,
    evidence_item: EvidenceItem,
    dependencies: ResolvedDependencies,
    claim_record: ClaimRecord,
) -> ReferenceProfileEvidenceCarrierItem:
    source = evidence_item.source
    if source.mode is ContentLocatorMode.INLINE_JSON:
        if source.inline_json is None:
            raise ResolveFailureError(
                message="reference-profile inline evidence has no content."
            )
        return ReferenceProfileEvidenceCarrierItem(
            evidence_identifier=str(evidence_item.evidence_identifier),
            evidence_kind_identifier=str(evidence_item.evidence_kind_identifier),
            source_json_content=source.inline_json.to_compatible_value(),
            source_media_type=source.media_type,
            source_preserved_octets=None,
            parameters=evidence_item.parameters,
        )
    if source.mode is not ContentLocatorMode.PACKAGE_MEMBER:
        raise ResolveFailureError(
            message=(
                "reference-profile evidence has unsupported locator mode "
                f"{source.mode!r}."
            )
        )
    if source.member_name is None:
        raise ResolveFailureError(
            message="reference-profile package-member evidence has no member name."
        )
    inventory_entry = claim_record.member_inventory.entry_for_name(
        member_name=source.member_name
    )
    canonical_reference = inventory_entry.canonical_reference
    if canonical_reference is None:
        raise ResolveFailureError(
            message=(
                "reference-profile package-member evidence has no canonical reference."
            )
        )
    dependency = dependencies.member_for_reference(
        canonical_reference=canonical_reference
    )
    if dependency is None:
        raise ResolveFailureError(
            message="reference-profile evidence dependency was not resolved.",
            related_reference=canonical_reference,
        )
    preserved_octets = dependency.preserved_bytes
    json_outcome = validate_json_representation(preserved_octets)
    return ReferenceProfileEvidenceCarrierItem(
        evidence_identifier=str(evidence_item.evidence_identifier),
        evidence_kind_identifier=str(evidence_item.evidence_kind_identifier),
        source_json_content=(json_outcome.value if json_outcome.accepted else None),
        source_media_type=source.media_type,
        source_preserved_octets=preserved_octets,
        parameters=evidence_item.parameters,
    )
