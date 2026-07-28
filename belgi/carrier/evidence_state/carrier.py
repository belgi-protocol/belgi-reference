"""Evidence-state carrier construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from belgi.carrier.exceptions import EvidenceCarrierError
from belgi.carrier.integrity import canonical_json_document_bytes
from belgi.carrier.inventory import (
    ContentLocator,
    DeclarationParameter,
    JsonCompatible,
    MemberName,
    ReferenceResolver,
    carrier_schema_designator,
    dedupe_member_names,
)

__all__ = [
    "EVIDENCE_STATE_CARRIER_MEDIA_TYPE",
    "EVIDENCE_STATE_CARRIER_SCHEMA_DESIGNATOR",
    "EvidenceIdentifier",
    "EvidenceItem",
    "EvidenceKindIdentifier",
    "EvidenceStateCarrier",
]


EVIDENCE_STATE_CARRIER_MEDIA_TYPE = "application/vnd.belgi.evidence-state-carrier+json"
EVIDENCE_STATE_CARRIER_SCHEMA_DESIGNATOR = carrier_schema_designator(
    schema_name="EvidenceStateCarrier.schema.json"
)

EvidenceIdentifier = NewType("EvidenceIdentifier", str)
EvidenceKindIdentifier = NewType("EvidenceKindIdentifier", str)


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceItem:
    """One preserved evidence binding inside an evidence-state carrier."""

    evidence_identifier: EvidenceIdentifier
    evidence_kind_identifier: EvidenceKindIdentifier
    source: ContentLocator
    parameters: tuple[DeclarationParameter, ...] = ()

    def __post_init__(self) -> None:
        if str(self.evidence_identifier).strip() == "":
            raise EvidenceCarrierError("evidence_identifier must be non-empty.")
        if str(self.evidence_kind_identifier).strip() == "":
            raise EvidenceCarrierError("evidence_kind_identifier must be non-empty.")

    def referenced_member_names(self) -> tuple[MemberName, ...]:
        return self.source.referenced_member_names()

    def to_json_object(
        self,
        *,
        resolve_reference: ReferenceResolver,
        include_identifier: bool = False,
    ) -> dict[str, JsonCompatible]:
        payload: dict[str, JsonCompatible] = {
            "evidenceKindIdentifier": str(self.evidence_kind_identifier),
            "source": self.source.to_json_object(resolve_reference=resolve_reference),
            "parameters": [parameter.to_json_object() for parameter in self.parameters],
        }
        if include_identifier:
            payload["evidenceIdentifier"] = str(self.evidence_identifier)
        return payload


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceStateCarrier:
    """Replay-relevant evidence-state carrier preserving the evidence state inputs."""

    evidence_items: tuple[EvidenceItem, ...]

    def __post_init__(self) -> None:
        seen_identifiers: set[EvidenceIdentifier] = set()
        for evidence_item in self.evidence_items:
            if evidence_item.evidence_identifier in seen_identifiers:
                raise EvidenceCarrierError(
                    f"Duplicate evidence identifier: {evidence_item.evidence_identifier}"
                )
            seen_identifiers.add(evidence_item.evidence_identifier)

    def referenced_member_names(self) -> tuple[MemberName, ...]:
        collected: list[MemberName] = []
        for evidence_item in self.evidence_items:
            collected.extend(evidence_item.referenced_member_names())
        return dedupe_member_names(member_names=tuple(collected))

    def content_locators(self) -> tuple[ContentLocator, ...]:
        return tuple(evidence_item.source for evidence_item in self.evidence_items)

    def to_json_object(
        self,
        *,
        resolve_reference: ReferenceResolver,
    ) -> dict[str, JsonCompatible]:
        evidence_items: dict[str, JsonCompatible] = {}
        for evidence_item in self.evidence_items:
            evidence_items[str(evidence_item.evidence_identifier)] = (
                evidence_item.to_json_object(
                    resolve_reference=resolve_reference,
                )
            )
        return {
            "kind": "evidence-state-carrier",
            "evidenceItems": evidence_items,
        }

    def to_json_bytes(
        self,
        *,
        resolve_reference: ReferenceResolver,
    ) -> bytes:
        return canonical_json_document_bytes(
            document=self.to_json_object(resolve_reference=resolve_reference)
        )
