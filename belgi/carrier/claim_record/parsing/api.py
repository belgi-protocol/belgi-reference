from __future__ import annotations

from belgi.carrier.claim_record.model import ClaimRecord, RootDesignators
from belgi.carrier.claim_record.parsing.dependencies import (
    parse_dependency_declarations,
)
from belgi.carrier.claim_record.parsing.document import (
    parse_claim_record_document,
    parse_claim_record_document_fields,
    validate_root_designator_payload,
)
from belgi.carrier.claim_record.parsing.inventory import (
    parse_member_inventory_entries,
)
from belgi.carrier.claim_record.parsing.sources import parse_referenced_sources
from belgi.carrier.inventory import MemberInventory

__all__ = ["parse_claim_record_bytes", "parse_claim_record_bytes_for_replay_read"]


def parse_claim_record_bytes(*, claim_record_bytes: bytes) -> ClaimRecord:
    return _parse_claim_record_bytes(
        claim_record_bytes=claim_record_bytes,
        validate_for_construction=True,
    )


def parse_claim_record_bytes_for_replay_read(
    *,
    claim_record_bytes: bytes,
) -> ClaimRecord:
    return _parse_claim_record_bytes(
        claim_record_bytes=claim_record_bytes,
        validate_for_construction=False,
    )


def _parse_claim_record_bytes(
    *,
    claim_record_bytes: bytes,
    validate_for_construction: bool,
) -> ClaimRecord:
    payload = parse_claim_record_document(claim_record_bytes=claim_record_bytes)
    member_inventory_entries = parse_member_inventory_entries(
        value=payload.get("memberInventory")
    )
    root_designator_payload = validate_root_designator_payload(
        value=payload.get("rootDesignators")
    )
    dependency_declarations = parse_dependency_declarations(
        value=payload.get("dependencyDeclarations")
    )
    referenced_sources = parse_referenced_sources(
        value=payload.get("referencedSources")
    )
    fields = parse_claim_record_document_fields(
        payload=payload,
        root_designators=root_designator_payload,
    )
    if validate_for_construction:
        return ClaimRecord(
            package_identifier=fields.package_identifier,
            root_designators=RootDesignators(
                judged_object_carrier_reference=fields.judged_object_carrier_reference,
                evidence_state_carrier_reference=(
                    fields.evidence_state_carrier_reference
                ),
                evaluator_carrier_reference=fields.evaluator_carrier_reference,
            ),
            member_inventory=MemberInventory(entries=member_inventory_entries),
            dependency_declarations=dependency_declarations,
            referenced_sources=referenced_sources,
            package_integrity_manifest_member_name=fields.package_integrity_manifest,
            package_integrity_anchor_member_name=fields.package_integrity_anchor,
            notes=fields.notes,
            cached_verdict=fields.cached_verdict,
        )
    return ClaimRecord.from_preserved_read(
        package_identifier=fields.package_identifier,
        root_designators=RootDesignators.from_preserved_read(
            judged_object_carrier_reference=fields.judged_object_carrier_reference,
            evidence_state_carrier_reference=fields.evidence_state_carrier_reference,
            evaluator_carrier_reference=fields.evaluator_carrier_reference,
        ),
        member_inventory=MemberInventory.from_preserved_read(
            entries=member_inventory_entries
        ),
        dependency_declarations=dependency_declarations,
        referenced_sources=referenced_sources,
        package_integrity_manifest_member_name=fields.package_integrity_manifest,
        package_integrity_anchor_member_name=fields.package_integrity_anchor,
        notes=fields.notes,
        cached_verdict=fields.cached_verdict,
    )
