from __future__ import annotations

from belgi.profile.governance import EvidenceKindId

__all__ = [
    "ALL_EVIDENCE_KINDS",
    "COVERAGE_REPORT",
    "DEPENDENCY_AUDIT_REPORT",
    "LINT_REPORT",
    "LOCK_RESOLUTION_REPORT",
    "TEST_REPORT",
    "TYPE_CHECK_REPORT",
]


LINT_REPORT = EvidenceKindId("belgi.python.evidence.lint-report")
COVERAGE_REPORT = EvidenceKindId("belgi.python.evidence.coverage-report")
TYPE_CHECK_REPORT = EvidenceKindId("belgi.python.evidence.type-check-report")
LOCK_RESOLUTION_REPORT = EvidenceKindId("belgi.python.evidence.lock-resolution-report")
TEST_REPORT = EvidenceKindId("belgi.python.evidence.test-report")
DEPENDENCY_AUDIT_REPORT = EvidenceKindId(
    "belgi.python.evidence.dependency-audit-report"
)

ALL_EVIDENCE_KINDS: tuple[EvidenceKindId, ...] = (
    LINT_REPORT,
    COVERAGE_REPORT,
    TYPE_CHECK_REPORT,
    LOCK_RESOLUTION_REPORT,
    TEST_REPORT,
    DEPENDENCY_AUDIT_REPORT,
)
