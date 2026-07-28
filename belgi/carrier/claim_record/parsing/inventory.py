from __future__ import annotations

from belgi.carrier.exceptions import ClaimRecordError
from belgi.carrier.inventory import (
    CanonicalReference,
    MemberClassification,
    MemberInventoryEntry,
    MemberName,
    MemberRole,
    RepresentationBinding,
)
from belgi.carrier.parse_support import (
    parse_immutable_designator_object,
    require_allowed_keys,
    require_mapping_object,
    require_non_empty_text,
)

__all__ = ["parse_member_inventory_entries"]


def parse_member_inventory_entries(
    *, value: object
) -> tuple[MemberInventoryEntry, ...]:
    payload = require_mapping_object(
        value=value,
        label="claim record.memberInventory",
        error_type=ClaimRecordError,
    )
    entries: list[MemberInventoryEntry] = []
    for member_name_text, entry_payload in payload.items():
        if not isinstance(member_name_text, str):
            raise ClaimRecordError("memberInventory keys must be member names.")
        entries.append(
            _parse_member_inventory_entry(
                member_name_text=member_name_text,
                value=entry_payload,
            )
        )
    return tuple(entries)


def _parse_member_inventory_entry(
    *,
    member_name_text: str,
    value: object,
) -> MemberInventoryEntry:
    label = f"memberInventory.{member_name_text}"
    payload = require_mapping_object(
        value=value,
        label=label,
        error_type=ClaimRecordError,
    )
    require_allowed_keys(
        payload=payload,
        label=label,
        allowed_keys=frozenset(
            {
                "memberRole",
                "classification",
                "representation",
                "canonicalReference",
                "projectionRuleIdentifier",
                "projectionRuleDesignator",
            }
        ),
        error_type=ClaimRecordError,
    )
    projection_rule_payload = payload.get("projectionRuleDesignator")
    projection_rule_identifier_payload = payload.get("projectionRuleIdentifier")
    projection_rule_designator = (
        parse_immutable_designator_object(
            value=projection_rule_payload,
            label=f"{label}.projectionRuleDesignator",
            error_type=ClaimRecordError,
        )
        if projection_rule_payload is not None
        else None
    )
    canonical_reference = payload.get("canonicalReference")
    return MemberInventoryEntry(
        member_name=MemberName(member_name_text),
        member_role=MemberRole(
            require_non_empty_text(
                value=payload.get("memberRole"),
                label=f"{label}.memberRole",
                error_type=ClaimRecordError,
            )
        ),
        classification=MemberClassification(
            require_non_empty_text(
                value=payload.get("classification"),
                label=f"{label}.classification",
                error_type=ClaimRecordError,
            )
        ),
        representation=_parse_representation_binding_object(
            value=payload.get("representation"),
            label=f"{label}.representation",
        ),
        canonical_reference=(
            CanonicalReference(
                require_non_empty_text(
                    value=canonical_reference,
                    label=f"{label}.canonicalReference",
                    error_type=ClaimRecordError,
                )
            )
            if canonical_reference is not None
            else None
        ),
        projection_rule_identifier=(
            require_non_empty_text(
                value=projection_rule_identifier_payload,
                label=f"{label}.projectionRuleIdentifier",
                error_type=ClaimRecordError,
            )
            if projection_rule_identifier_payload is not None
            else None
        ),
        projection_rule_designator=projection_rule_designator,
    )


def _parse_representation_binding_object(
    *,
    value: object,
    label: str,
) -> RepresentationBinding:
    payload = require_mapping_object(
        value=value,
        label=label,
        error_type=ClaimRecordError,
    )
    require_allowed_keys(
        payload=payload,
        label=label,
        allowed_keys=frozenset({"mediaType", "schemaDesignator"}),
        error_type=ClaimRecordError,
    )
    schema_designator_payload = payload.get("schemaDesignator")
    schema_designator = (
        parse_immutable_designator_object(
            value=schema_designator_payload,
            label=f"{label}.schemaDesignator",
            error_type=ClaimRecordError,
        )
        if schema_designator_payload is not None
        else None
    )
    return RepresentationBinding(
        media_type=require_non_empty_text(
            value=payload.get("mediaType"),
            label=f"{label}.mediaType",
            error_type=ClaimRecordError,
        ),
        schema_designator=schema_designator,
    )
