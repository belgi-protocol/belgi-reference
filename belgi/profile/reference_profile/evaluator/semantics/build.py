from __future__ import annotations

from typing import TYPE_CHECKING, cast

from belgi.profile.exceptions import ProfileError
from belgi.profile.reference_profile.declarations import (
    EvidenceOutcome,
    OutcomePolicyDeclaration,
)
from belgi.profile.reference_profile.evidence.semantics import (
    bound_evidence_items,
    unwrap_profile_declaration,
)
from belgi.profile.reference_profile.evidence.subject_access import subject_field
from belgi.profile.vocabulary.tolerances import SeverityLevel

if TYPE_CHECKING:
    from belgi.core import EvidenceState, JudgedObject


__all__ = [
    "build_policy_sat",
    "evaluate_outcome_policy",
    "satisfies_build_policy",
]


def _normalize_outcome(item: object) -> EvidenceOutcome | None:
    boolean_fields = (
        ("passed", EvidenceOutcome.PASS, EvidenceOutcome.FAIL),
        ("clean", EvidenceOutcome.PASS, EvidenceOutcome.FAIL),
        ("success", EvidenceOutcome.PASS, EvidenceOutcome.FAIL),
    )
    for field_name, true_value, false_value in boolean_fields:
        value = subject_field(item, field_name)
        if isinstance(value, bool):
            return true_value if value else false_value
    outcome = subject_field(item, "outcome", "status", "state", "result")
    if outcome is None:
        return None
    normalized = str(outcome).strip().lower().replace("_", "-")
    mapping = {
        "pass": EvidenceOutcome.PASS,
        "passed": EvidenceOutcome.PASS,
        "success": EvidenceOutcome.PASS,
        "succeeded": EvidenceOutcome.PASS,
        "ok": EvidenceOutcome.PASS,
        "clean": EvidenceOutcome.PASS,
        "fail": EvidenceOutcome.FAIL,
        "failed": EvidenceOutcome.FAIL,
        "error": EvidenceOutcome.FAIL,
        "no-go": EvidenceOutcome.FAIL,
        "warn": EvidenceOutcome.WARN,
        "warning": EvidenceOutcome.WARN,
        "warnings": EvidenceOutcome.WARN,
        "block": EvidenceOutcome.BLOCK,
        "blocked": EvidenceOutcome.BLOCK,
    }
    return mapping.get(normalized)


def _numeric_value(item: object) -> float | None:
    for field_name in ("numeric_value", "value", "coverage", "score", "percentage"):
        value = subject_field(item, field_name)
        if value is None:
            continue
        if isinstance(value, (int, float)):
            return float(value)
    return None


_SEVERITY_ORDER = {
    SeverityLevel.NONE: 0,
    SeverityLevel.LOW: 1,
    SeverityLevel.MODERATE: 2,
    SeverityLevel.HIGH: 3,
    SeverityLevel.CRITICAL: 4,
}


def _severity_value(item: object) -> SeverityLevel | None:
    severity = subject_field(item, "severity", "maximum_severity")
    if severity is None:
        return None
    text = str(severity).strip().lower()
    for candidate in SeverityLevel:
        if candidate.value == text:
            return candidate
    return None


def _failure_count(item: object) -> int | None:
    for field_name in ("failure_count", "failed_cases", "failures", "failed_tests"):
        value = subject_field(item, field_name)
        if isinstance(value, int):
            return value
    return None


def evaluate_outcome_policy(
    *,
    evidence_state: object,
    declaration: OutcomePolicyDeclaration,
) -> bool:
    accepted_outcomes = set(declaration.accepted_outcomes)
    for binding in declaration.required_bindings:
        items = bound_evidence_items(
            evidence_state=evidence_state,
            binding=binding,
            condition=declaration,
        )
        if len(items) < binding.minimum_count:
            return False
        for item in items:
            outcome = _normalize_outcome(item)
            if outcome is None or outcome not in accepted_outcomes:
                return False
            numeric_value = _numeric_value(item)
            if declaration.minimum_numeric_value is not None:
                if (
                    numeric_value is None
                    or numeric_value < declaration.minimum_numeric_value
                ):
                    return False
            if declaration.maximum_numeric_value is not None:
                if (
                    numeric_value is None
                    or numeric_value > declaration.maximum_numeric_value
                ):
                    return False
            if declaration.maximum_severity is not None:
                severity = _severity_value(item)
                if severity is None:
                    return False
                if (
                    _SEVERITY_ORDER[severity]
                    > _SEVERITY_ORDER[declaration.maximum_severity]
                ):
                    return False
            if declaration.maximum_failed_cases is not None:
                failed_cases = _failure_count(item)
                if (
                    failed_cases is None
                    or failed_cases > declaration.maximum_failed_cases
                ):
                    return False
    return True


def satisfies_build_policy(
    *,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
    condition: object,
) -> bool:
    del judged_object
    declaration = unwrap_profile_declaration(condition, OutcomePolicyDeclaration)
    return evaluate_outcome_policy(
        evidence_state=evidence_state,
        declaration=declaration,
    )


def build_policy_sat(
    judged_object: object,
    evidence_state: object,
    condition: object,
) -> bool:
    try:
        return satisfies_build_policy(
            judged_object=cast("JudgedObject", judged_object),
            evidence_state=cast("EvidenceState", evidence_state),
            condition=condition,
        )
    except (AttributeError, ProfileError, ValueError):
        return False
