from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.reference_profile.identifiers.evidence_kinds import REVIEW_RECORD
from belgi.profile.reference_profile.identifiers.parameters import (
    EVIDENCE_SOURCE_CLASS_PARAMETER,
)

__all__ = [
    "PART4_EVIDENCE_SOURCE_CLASS_PARAMETER",
    "REVIEW_RECORD_FIELDS",
    "REVIEW_RECORD_IDENTIFIER",
    "normalize_reference_profile_review_record",
]


REVIEW_RECORD_IDENTIFIER = str(REVIEW_RECORD)
PART4_EVIDENCE_SOURCE_CLASS_PARAMETER = str(EVIDENCE_SOURCE_CLASS_PARAMETER)
REVIEW_RECORD_FIELDS = (
    "reviewIdentifier",
    "proposalIdentifier",
    "proposedSourceStateIdentifier",
    "baselineRevisionIdentifier",
    "baselineSourceStateIdentifier",
    "decision",
)
_REVIEW_RECORD_FIELD_SET = frozenset(REVIEW_RECORD_FIELDS)


def normalize_reference_profile_review_record(
    *, document: Mapping[str, object], label: str
) -> dict[str, str]:
    if set(document) != _REVIEW_RECORD_FIELD_SET:
        raise ValueError(
            f"{label} must contain exactly the closed six-member ReviewRecord."
        )
    record: dict[str, str] = {}
    for field_name in REVIEW_RECORD_FIELDS:
        value = document.get(field_name)
        if not isinstance(value, str) or not value:
            raise ValueError(f"{label}.{field_name} must be a non-empty exact string.")
        record[field_name] = value
    if record["decision"] not in {"accepted", "rejected"}:
        raise ValueError(f"{label}.decision must be 'accepted' or 'rejected'.")
    return record
