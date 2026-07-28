from __future__ import annotations

from belgi.carrier import (
    ClaimRecord,
    EvidenceIdentifier,
    EvidenceKindIdentifier,
    EvidenceStateCarrier,
)
from belgi.carrier import (
    EvidenceItem as CarrierEvidenceItem,
)
from belgi.carrier.json_representation import TrustedJSONRole
from belgi.replay.lifting.parsing import (
    load_trusted_carrier_json_object,
    require_string,
)
from belgi.replay.parsing import (
    content_locator_from_payload,
    parse_declaration_parameters,
    require_json_mapping,
)

__all__ = ["parse_evidence_state_carrier"]


def parse_evidence_state_carrier(
    *,
    root_bytes: bytes,
    description: str,
    claim_record: ClaimRecord,
) -> EvidenceStateCarrier:
    payload = load_trusted_carrier_json_object(
        octets=root_bytes,
        description=description,
        trusted_role=TrustedJSONRole.EVIDENCE_STATE,
    )
    evidence_items_payload = require_json_mapping(
        value=payload.get("evidenceItems"),
        description=f"{description}.evidenceItems",
    )
    evidence_items: list[CarrierEvidenceItem] = []
    for evidence_identifier, raw_evidence_item in sorted(
        evidence_items_payload.items()
    ):
        evidence_item = require_json_mapping(
            value=raw_evidence_item,
            description=f"{description}.evidenceItems.{evidence_identifier}",
        )
        evidence_items.append(
            CarrierEvidenceItem(
                evidence_identifier=EvidenceIdentifier(evidence_identifier),
                evidence_kind_identifier=EvidenceKindIdentifier(
                    require_string(
                        obj=evidence_item,
                        key="evidenceKindIdentifier",
                        description=f"{description}.evidenceItems.{evidence_identifier}",
                    )
                ),
                source=content_locator_from_payload(
                    payload=evidence_item.get("source"),
                    description=f"{description}.evidenceItems.{evidence_identifier}.source",
                    claim_record=claim_record,
                ),
                parameters=parse_declaration_parameters(
                    payload=evidence_item.get("parameters"),
                    description=f"{description}.evidenceItems.{evidence_identifier}.parameters",
                ),
            )
        )
    return EvidenceStateCarrier(evidence_items=tuple(evidence_items))
