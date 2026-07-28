"""Reserved replay-package member names."""

from __future__ import annotations

from belgi.carrier.inventory import MemberName

CLAIM_RECORD_MEMBER_NAME = MemberName("claim-record")
PACKAGE_INTEGRITY_MANIFEST_MEMBER_NAME = MemberName("package-integrity-manifest")
PACKAGE_INTEGRITY_ANCHOR_MEMBER_NAME = MemberName("package-integrity-anchor")
JUDGED_ROOT_MEMBER_NAME = MemberName("judged-object-carrier-root")
EVIDENCE_ROOT_MEMBER_NAME = MemberName("evidence-state-carrier-root")
EVALUATOR_ROOT_MEMBER_NAME = MemberName("evaluator-carrier-root")

__all__ = [
    "CLAIM_RECORD_MEMBER_NAME",
    "EVALUATOR_ROOT_MEMBER_NAME",
    "EVIDENCE_ROOT_MEMBER_NAME",
    "JUDGED_ROOT_MEMBER_NAME",
    "PACKAGE_INTEGRITY_ANCHOR_MEMBER_NAME",
    "PACKAGE_INTEGRITY_MANIFEST_MEMBER_NAME",
]
