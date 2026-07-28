"""Judged-object carrier construction."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier.integrity import canonical_json_document_bytes
from belgi.carrier.inventory import (
    ContentLocator,
    JsonCompatible,
    MemberName,
    ReferenceResolver,
    carrier_schema_designator,
    dedupe_member_names,
)

__all__ = [
    "JUDGED_OBJECT_CARRIER_MEDIA_TYPE",
    "JUDGED_OBJECT_CARRIER_SCHEMA_DESIGNATOR",
    "JudgedObjectCarrier",
]


JUDGED_OBJECT_CARRIER_MEDIA_TYPE = "application/vnd.belgi.judged-object-carrier+json"
JUDGED_OBJECT_CARRIER_SCHEMA_DESIGNATOR = carrier_schema_designator(
    schema_name="JudgedObjectCarrier.schema.json"
)


@dataclass(frozen=True, slots=True, kw_only=True)
class JudgedObjectCarrier:
    """Replay-relevant judged-object carrier preserving one proposal and one baseline."""

    proposal: ContentLocator
    baseline: ContentLocator

    def referenced_member_names(self) -> tuple[MemberName, ...]:
        return dedupe_member_names(
            member_names=(
                self.proposal.referenced_member_names()
                + self.baseline.referenced_member_names()
            )
        )

    def content_locators(self) -> tuple[ContentLocator, ...]:
        return (self.proposal, self.baseline)

    def to_json_object(
        self,
        *,
        resolve_reference: ReferenceResolver,
    ) -> dict[str, JsonCompatible]:
        return {
            "kind": "judged-object-carrier",
            "proposal": self.proposal.to_json_object(
                resolve_reference=resolve_reference
            ),
            "baseline": self.baseline.to_json_object(
                resolve_reference=resolve_reference
            ),
        }

    def to_json_bytes(
        self,
        *,
        resolve_reference: ReferenceResolver,
    ) -> bytes:
        return canonical_json_document_bytes(
            document=self.to_json_object(resolve_reference=resolve_reference)
        )
