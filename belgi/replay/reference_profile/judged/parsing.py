from __future__ import annotations

from belgi.carrier import ClaimRecord, JudgedObjectCarrier
from belgi.carrier.json_representation import TrustedJSONRole
from belgi.replay.lifting.parsing import (
    load_trusted_carrier_json_object,
)
from belgi.replay.parsing import content_locator_from_payload

__all__ = ["parse_judged_object_carrier"]


def parse_judged_object_carrier(
    *,
    root_bytes: bytes,
    description: str,
    claim_record: ClaimRecord,
) -> JudgedObjectCarrier:
    payload = load_trusted_carrier_json_object(
        octets=root_bytes,
        description=description,
        trusted_role=TrustedJSONRole.JUDGED_OBJECT,
    )
    return JudgedObjectCarrier(
        proposal=content_locator_from_payload(
            payload=payload.get("proposal"),
            description=f"{description}.proposal",
            claim_record=claim_record,
        ),
        baseline=content_locator_from_payload(
            payload=payload.get("baseline"),
            description=f"{description}.baseline",
            claim_record=claim_record,
        ),
    )
