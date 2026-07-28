"""Step-2 applicability view over bounded claim-record bootstrap payloads."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier import (
    CanonicalReference,
    ClaimRecordBootstrapEntry,
    ClaimRecordError,
    ImmutableDesignator,
)
from belgi.carrier.parse_support import (
    parse_immutable_designator_object,
    require_non_empty_text,
)

__all__ = ["BootstrapMemberObservation", "observe_bootstrap_member"]


@dataclass(frozen=True, slots=True, kw_only=True)
class BootstrapMemberObservation:
    member_name: str
    member_role: str
    classification: str
    media_type: str
    schema_designator: ImmutableDesignator | None
    canonical_reference: CanonicalReference | None


def observe_bootstrap_member(
    *, entry: ClaimRecordBootstrapEntry
) -> BootstrapMemberObservation:
    """Decode only fields needed to decide step-2 applicability.

    Unknown fields and later-step metadata remain deliberately unexamined until
    complete authenticated representation validation at step 4.
    """

    label = f"claim record bootstrap.memberInventory.{entry.member_name!s}"
    schema_payload = entry.schema_designator_payload
    canonical_reference_payload = entry.canonical_reference_payload
    return BootstrapMemberObservation(
        member_name=str(entry.member_name),
        member_role=require_non_empty_text(
            value=entry.member_role_payload,
            label=f"{label}.memberRole",
            error_type=ClaimRecordError,
        ),
        classification=require_non_empty_text(
            value=entry.classification_payload,
            label=f"{label}.classification",
            error_type=ClaimRecordError,
        ),
        media_type=require_non_empty_text(
            value=entry.media_type_payload,
            label=f"{label}.representation.mediaType",
            error_type=ClaimRecordError,
        ),
        schema_designator=(
            parse_immutable_designator_object(
                value=schema_payload,
                label=f"{label}.representation.schemaDesignator",
                error_type=ClaimRecordError,
            )
            if schema_payload is not None
            else None
        ),
        canonical_reference=(
            CanonicalReference(
                require_non_empty_text(
                    value=canonical_reference_payload,
                    label=f"{label}.canonicalReference",
                    error_type=ClaimRecordError,
                )
            )
            if canonical_reference_payload is not None
            else None
        ),
    )
