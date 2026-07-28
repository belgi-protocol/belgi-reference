from __future__ import annotations

from belgi.profile.governance import ConditionId

__all__ = [
    "ALL_CONDITIONS",
    "ANALYSIS_POLICY_SATISFIED",
    "BUILD_POLICY_SATISFIED",
    "CHANGE_BASIS_RESOLVED",
    "COVERAGE_POLICY_SATISFIED",
    "DEPENDENCY_POLICY_SATISFIED",
    "ENVIRONMENT_COMPATIBILITY_SATISFIED",
    "FOUNDATION_CONDITIONS",
    "REQUIRED_EVIDENCE_PRESENT",
    "REVIEW_POLICY_SATISFIED",
    "TEST_POLICY_SATISFIED",
    "normalize_reference_profile_condition_identifier",
]


CHANGE_BASIS_RESOLVED = ConditionId(
    "belgi.software-change.condition.change-basis-resolved"
)
REQUIRED_EVIDENCE_PRESENT = ConditionId(
    "belgi.software-change.condition.required-evidence-present"
)
BUILD_POLICY_SATISFIED = ConditionId(
    "belgi.software-change.condition.build-policy-satisfied"
)
TEST_POLICY_SATISFIED = ConditionId(
    "belgi.software-change.condition.test-policy-satisfied"
)
COVERAGE_POLICY_SATISFIED = ConditionId(
    "belgi.software-change.condition.coverage-policy-satisfied"
)
REVIEW_POLICY_SATISFIED = ConditionId(
    "belgi.software-change.condition.review-policy-satisfied"
)
DEPENDENCY_POLICY_SATISFIED = ConditionId(
    "belgi.software-change.condition.dependency-policy-satisfied"
)
ANALYSIS_POLICY_SATISFIED = ConditionId(
    "belgi.software-change.condition.analysis-policy-satisfied"
)
ENVIRONMENT_COMPATIBILITY_SATISFIED = ConditionId(
    "belgi.software-change.condition.environment-compatibility-satisfied"
)

ALL_CONDITIONS: tuple[ConditionId, ...] = (
    CHANGE_BASIS_RESOLVED,
    REQUIRED_EVIDENCE_PRESENT,
    BUILD_POLICY_SATISFIED,
    TEST_POLICY_SATISFIED,
    COVERAGE_POLICY_SATISFIED,
    REVIEW_POLICY_SATISFIED,
    DEPENDENCY_POLICY_SATISFIED,
    ANALYSIS_POLICY_SATISFIED,
    ENVIRONMENT_COMPATIBILITY_SATISFIED,
)

FOUNDATION_CONDITIONS: tuple[ConditionId, ...] = (
    CHANGE_BASIS_RESOLVED,
    REQUIRED_EVIDENCE_PRESENT,
)


def normalize_reference_profile_condition_identifier(*, value: str) -> ConditionId:
    if not value:
        raise ValueError("condition identifier must not be empty.")
    condition_id = ConditionId(value)
    if condition_id not in ALL_CONDITIONS:
        raise ValueError(f"unsupported condition identifier: {value!r}.")
    return condition_id
