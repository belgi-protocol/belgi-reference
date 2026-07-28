from __future__ import annotations

from belgi.profile.governance import ConditionId

__all__ = [
    "ALL_CONDITIONS",
    "COVERAGE_THRESHOLD_MET",
    "DEPENDENCY_AUDIT_PASS",
    "LINT_CLEAN",
    "LOCK_RESOLUTION_CLEAN",
    "TESTS_PASS",
    "TYPE_CHECK_PASS",
]


LINT_CLEAN = ConditionId("belgi.python.condition.lint-clean")
COVERAGE_THRESHOLD_MET = ConditionId("belgi.python.condition.coverage-threshold-met")
TYPE_CHECK_PASS = ConditionId("belgi.python.condition.type-check-pass")
LOCK_RESOLUTION_CLEAN = ConditionId("belgi.python.condition.lock-resolution-clean")
TESTS_PASS = ConditionId("belgi.python.condition.tests-pass")
DEPENDENCY_AUDIT_PASS = ConditionId("belgi.python.condition.dependency-audit-pass")

ALL_CONDITIONS: tuple[ConditionId, ...] = (
    LINT_CLEAN,
    COVERAGE_THRESHOLD_MET,
    TYPE_CHECK_PASS,
    LOCK_RESOLUTION_CLEAN,
    TESTS_PASS,
    DEPENDENCY_AUDIT_PASS,
)
