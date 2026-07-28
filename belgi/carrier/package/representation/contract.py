"""Physical replay-package representation contract values."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "BASELINE_ENVELOPE",
    "FIXED_MEMBER_BINDINGS",
    "FixedMemberBinding",
    "PackageResourceEnvelope",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class PackageResourceEnvelope:
    outer_zip_bytes: int
    directory_entry_count: int
    member_count: int
    member_bytes: int
    claim_record_bytes: int
    total_member_bytes: int
    path_segments: int
    path_segment_bytes: int
    path_bytes: int
    claim_record_json_nesting_depth: int


BASELINE_ENVELOPE = PackageResourceEnvelope(
    outer_zip_bytes=536_870_912,
    directory_entry_count=131_072,
    member_count=4_096,
    member_bytes=67_108_864,
    claim_record_bytes=8_388_608,
    total_member_bytes=268_435_456,
    path_segments=32,
    path_segment_bytes=255,
    path_bytes=1_024,
    claim_record_json_nesting_depth=128,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class FixedMemberBinding:
    logical_name: str
    physical_path: str
    member_role: str
    classification: str
    trusted_json_role: str


FIXED_MEMBER_BINDINGS = (
    FixedMemberBinding(
        logical_name="claim-record",
        physical_path="claim-record.json",
        member_role="claim-record",
        classification="replay-relevant",
        trusted_json_role="claim-record",
    ),
    FixedMemberBinding(
        logical_name="package-integrity-manifest",
        physical_path="package-integrity-manifest",
        member_role="package-integrity-manifest",
        classification="claim-record-integrity-recovery",
        trusted_json_role="package-integrity-manifest",
    ),
    FixedMemberBinding(
        logical_name="package-integrity-anchor",
        physical_path="package-integrity-anchor",
        member_role="package-integrity-anchor",
        classification="claim-record-integrity-recovery",
        trusted_json_role="package-integrity-anchor",
    ),
    FixedMemberBinding(
        logical_name="judged-object-carrier-root",
        physical_path="judged-object-carrier-root",
        member_role="judged-object-carrier-root",
        classification="replay-relevant",
        trusted_json_role="judged-object",
    ),
    FixedMemberBinding(
        logical_name="evidence-state-carrier-root",
        physical_path="evidence-state-carrier-root",
        member_role="evidence-state-carrier-root",
        classification="replay-relevant",
        trusted_json_role="evidence-state",
    ),
    FixedMemberBinding(
        logical_name="evaluator-carrier-root",
        physical_path="evaluator-carrier-root",
        member_role="evaluator-carrier-root",
        classification="replay-relevant",
        trusted_json_role="evaluator",
    ),
)
