from __future__ import annotations

from belgi.profile.governance import EvidenceKindId

__all__ = [
    "ALL_EVIDENCE_KINDS",
    "BUILD_RESULT",
    "COVERAGE_RESULT",
    "DEPENDENCY_ANALYSIS_RESULT",
    "ENVIRONMENT_RECORD",
    "PROVENANCE_RECORD",
    "REVIEW_RECORD",
    "STATIC_ANALYSIS_RESULT",
    "TEST_RESULT",
]


BUILD_RESULT = EvidenceKindId("belgi.software-change.evidence.build-result")
TEST_RESULT = EvidenceKindId("belgi.software-change.evidence.test-result")
COVERAGE_RESULT = EvidenceKindId("belgi.software-change.evidence.coverage-result")
STATIC_ANALYSIS_RESULT = EvidenceKindId(
    "belgi.software-change.evidence.static-analysis-result"
)
DEPENDENCY_ANALYSIS_RESULT = EvidenceKindId(
    "belgi.software-change.evidence.dependency-analysis-result"
)
REVIEW_RECORD = EvidenceKindId("belgi.software-change.evidence.review-record")
PROVENANCE_RECORD = EvidenceKindId("belgi.software-change.evidence.provenance-record")
ENVIRONMENT_RECORD = EvidenceKindId("belgi.software-change.evidence.environment-record")

ALL_EVIDENCE_KINDS: tuple[EvidenceKindId, ...] = (
    BUILD_RESULT,
    TEST_RESULT,
    COVERAGE_RESULT,
    STATIC_ANALYSIS_RESULT,
    DEPENDENCY_ANALYSIS_RESULT,
    REVIEW_RECORD,
    PROVENANCE_RECORD,
    ENVIRONMENT_RECORD,
)
