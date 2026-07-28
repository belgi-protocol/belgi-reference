from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from belgi.carrier.claim_record.model import CachedVerdict
from belgi.carrier.exceptions import ClaimRecordError
from belgi.carrier.inventory import (
    CanonicalReference,
    MemberName,
    PackageIdentifier,
    require_package_identifier,
)
from belgi.carrier.json_representation import (
    TrustedJSONRole,
    validate_carrier_json,
)
from belgi.carrier.parse_support import (
    require_allowed_keys,
    require_mapping_object,
    require_non_empty_text,
)

__all__ = [
    "ClaimRecordDocumentFields",
    "parse_claim_record_document",
    "parse_claim_record_document_fields",
    "validate_root_designator_payload",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class ClaimRecordDocumentFields:
    package_identifier: PackageIdentifier
    package_integrity_manifest: MemberName
    package_integrity_anchor: MemberName
    judged_object_carrier_reference: CanonicalReference
    evidence_state_carrier_reference: CanonicalReference
    evaluator_carrier_reference: CanonicalReference
    notes: tuple[str, ...]
    cached_verdict: CachedVerdict | None


def parse_claim_record_document(*, claim_record_bytes: bytes) -> dict[str, object]:
    outcome = validate_carrier_json(
        claim_record_bytes,
        trusted_role=TrustedJSONRole.CLAIM_RECORD,
    )
    if not outcome.accepted:
        if outcome.schema_issues:
            issue = next(
                (
                    candidate
                    for candidate in outcome.schema_issues
                    if candidate.keyword == "const" and candidate.path == "$.kind"
                ),
                outcome.schema_issues[0],
            )
            issue_path = (
                f"claim record{issue.path[1:]}"
                if issue.path.startswith("$")
                else issue.path
            )
            raise ClaimRecordError(
                f"claim record invalid at {issue_path}: {issue.message}"
            )
        raise ClaimRecordError(
            "claim record representation rejected at "
            f"{outcome.stage}: {outcome.result_code}."
        )
    if not isinstance(outcome.value, dict):
        raise ClaimRecordError("claim record must be a JSON object.")
    return outcome.value


def validate_root_designator_payload(*, value: object) -> Mapping[str, object]:
    payload = require_mapping_object(
        value=value,
        label="claim record.rootDesignators",
        error_type=ClaimRecordError,
    )
    require_allowed_keys(
        payload=payload,
        label="claim record.rootDesignators",
        allowed_keys=frozenset(
            {"judgedObjectCarrier", "evidenceStateCarrier", "evaluatorCarrier"}
        ),
        error_type=ClaimRecordError,
    )
    return payload


def parse_claim_record_document_fields(
    *,
    payload: Mapping[str, object],
    root_designators: Mapping[str, object],
) -> ClaimRecordDocumentFields:
    notes_payload = payload.get("notes", [])
    if not isinstance(notes_payload, list):
        raise ClaimRecordError("claim record.notes must be an array when present.")
    notes = tuple(
        require_non_empty_text(
            value=note,
            label="claim record.notes[]",
            error_type=ClaimRecordError,
        )
        for note in notes_payload
    )
    cached_verdict = _parse_cached_verdict(payload.get("cachedVerdict"))
    return ClaimRecordDocumentFields(
        package_identifier=require_package_identifier(
            value=payload.get("packageIdentifier"),
            label="claim record.packageIdentifier",
            error_type=ClaimRecordError,
        ),
        package_integrity_manifest=MemberName(
            require_non_empty_text(
                value=payload.get("packageIntegrityManifestMember"),
                label="claim record.packageIntegrityManifestMember",
                error_type=ClaimRecordError,
            )
        ),
        package_integrity_anchor=MemberName(
            require_non_empty_text(
                value=payload.get("packageIntegrityAnchorMember"),
                label="claim record.packageIntegrityAnchorMember",
                error_type=ClaimRecordError,
            )
        ),
        judged_object_carrier_reference=_root_designator(
            root_designators=root_designators,
            field="judgedObjectCarrier",
        ),
        evidence_state_carrier_reference=_root_designator(
            root_designators=root_designators,
            field="evidenceStateCarrier",
        ),
        evaluator_carrier_reference=_root_designator(
            root_designators=root_designators,
            field="evaluatorCarrier",
        ),
        notes=notes,
        cached_verdict=cached_verdict,
    )


def _parse_cached_verdict(value: object) -> CachedVerdict | None:
    if value is None:
        return None
    if value == 0:
        return 0
    if value == 1:
        return 1
    raise ClaimRecordError("cachedVerdict must be 0, 1, or absent.")


def _root_designator(
    *,
    root_designators: Mapping[str, object],
    field: str,
) -> CanonicalReference:
    return CanonicalReference(
        require_non_empty_text(
            value=root_designators.get(field),
            label=f"claim record.rootDesignators.{field}",
            error_type=ClaimRecordError,
        )
    )
