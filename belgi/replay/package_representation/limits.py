"""Baseline package-representation resource observations."""

from __future__ import annotations

from belgi.carrier.package.representation.contract import (
    BASELINE_ENVELOPE,
    PackageResourceEnvelope,
)

from .model import RepresentationResult, accepted_result, rejected_result

__all__ = ["check_resource_limit"]


def check_resource_limit(
    *,
    resource: str,
    observed: int,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> RepresentationResult:
    controls = {
        "outerZipBytes": (envelope.outer_zip_bytes, 1, "outer-size-exceeded"),
        "directoryEntryCount": (
            envelope.directory_entry_count,
            3,
            "entry-count-exceeded",
        ),
        "memberCount": (envelope.member_count, 3, "entry-count-exceeded"),
        "memberBytes": (envelope.member_bytes, 5, "member-size-exceeded"),
        "claimRecordBytes": (
            envelope.claim_record_bytes,
            6,
            "claim-record-size-exceeded",
        ),
        "totalMemberBytes": (
            envelope.total_member_bytes,
            5,
            "total-size-exceeded",
        ),
        "pathSegments": (envelope.path_segments, 4, "invalid-entry-name"),
        "pathSegmentBytes": (
            envelope.path_segment_bytes,
            4,
            "invalid-entry-name",
        ),
        "pathBytes": (envelope.path_bytes, 4, "invalid-entry-name"),
        "claimRecordJsonNestingDepth": (
            envelope.claim_record_json_nesting_depth,
            6,
            "invalid-claim-record-representation",
        ),
    }
    try:
        maximum, stage, result_code = controls[resource]
    except KeyError as exc:
        raise ValueError(
            f"unknown package-representation resource: {resource}"
        ) from exc
    if observed < 0:
        raise ValueError("resource observation must be non-negative")
    if observed > maximum:
        return rejected_result(stage=stage, result_code=result_code)
    return accepted_result((), stage=stage, result_code="within-limit")
