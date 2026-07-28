from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.edition import ExactEditionBinding
from belgi.profile.governance import ConditionId
from belgi.profile.reference_profile.identifiers.conditions import (
    ANALYSIS_POLICY_SATISFIED,
    BUILD_POLICY_SATISFIED,
    COVERAGE_POLICY_SATISFIED,
    DEPENDENCY_POLICY_SATISFIED,
    TEST_POLICY_SATISFIED,
)
from belgi.profile.vocabulary.tolerances import SeverityLevel

from .evidence import EvidenceOutcome, RequiredEvidenceBinding

__all__ = [
    "OutcomePolicyDeclaration",
    "analysis_policy_declaration",
    "build_policy_declaration",
    "coverage_policy_declaration",
    "dependency_policy_declaration",
    "test_policy_declaration",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class OutcomePolicyDeclaration:
    condition_id: ConditionId
    required_bindings: tuple[RequiredEvidenceBinding, ...]
    accepted_outcomes: tuple[EvidenceOutcome, ...]
    minimum_numeric_value: float | None
    maximum_numeric_value: float | None
    maximum_severity: SeverityLevel | None
    maximum_failed_cases: int | None
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...]

    def __post_init__(self) -> None:
        if not self.required_bindings:
            raise ValueError("required_bindings must not be empty.")
        if not self.accepted_outcomes:
            raise ValueError("accepted_outcomes must not be empty.")
        if (
            self.minimum_numeric_value is not None
            and self.maximum_numeric_value is not None
            and self.minimum_numeric_value > self.maximum_numeric_value
        ):
            raise ValueError(
                "minimum_numeric_value must not exceed maximum_numeric_value."
            )
        if self.maximum_failed_cases is not None and self.maximum_failed_cases < 0:
            raise ValueError("maximum_failed_cases must be non-negative.")


def build_policy_declaration(
    *,
    required_bindings: tuple[RequiredEvidenceBinding, ...],
    accepted_outcomes: tuple[EvidenceOutcome, ...],
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...],
) -> OutcomePolicyDeclaration:
    return OutcomePolicyDeclaration(
        condition_id=BUILD_POLICY_SATISFIED,
        required_bindings=required_bindings,
        accepted_outcomes=accepted_outcomes,
        minimum_numeric_value=None,
        maximum_numeric_value=None,
        maximum_severity=None,
        maximum_failed_cases=None,
        replay_relevant_dependencies=replay_relevant_dependencies,
    )


def test_policy_declaration(
    *,
    required_bindings: tuple[RequiredEvidenceBinding, ...],
    accepted_outcomes: tuple[EvidenceOutcome, ...],
    maximum_failed_cases: int | None,
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...],
) -> OutcomePolicyDeclaration:
    return OutcomePolicyDeclaration(
        condition_id=TEST_POLICY_SATISFIED,
        required_bindings=required_bindings,
        accepted_outcomes=accepted_outcomes,
        minimum_numeric_value=None,
        maximum_numeric_value=None,
        maximum_severity=None,
        maximum_failed_cases=maximum_failed_cases,
        replay_relevant_dependencies=replay_relevant_dependencies,
    )


def coverage_policy_declaration(
    *,
    required_bindings: tuple[RequiredEvidenceBinding, ...],
    accepted_outcomes: tuple[EvidenceOutcome, ...],
    minimum_numeric_value: float | None,
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...],
) -> OutcomePolicyDeclaration:
    return OutcomePolicyDeclaration(
        condition_id=COVERAGE_POLICY_SATISFIED,
        required_bindings=required_bindings,
        accepted_outcomes=accepted_outcomes,
        minimum_numeric_value=minimum_numeric_value,
        maximum_numeric_value=None,
        maximum_severity=None,
        maximum_failed_cases=None,
        replay_relevant_dependencies=replay_relevant_dependencies,
    )


def dependency_policy_declaration(
    *,
    required_bindings: tuple[RequiredEvidenceBinding, ...],
    accepted_outcomes: tuple[EvidenceOutcome, ...],
    maximum_severity: SeverityLevel | None,
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...],
) -> OutcomePolicyDeclaration:
    return OutcomePolicyDeclaration(
        condition_id=DEPENDENCY_POLICY_SATISFIED,
        required_bindings=required_bindings,
        accepted_outcomes=accepted_outcomes,
        minimum_numeric_value=None,
        maximum_numeric_value=None,
        maximum_severity=maximum_severity,
        maximum_failed_cases=None,
        replay_relevant_dependencies=replay_relevant_dependencies,
    )


def analysis_policy_declaration(
    *,
    required_bindings: tuple[RequiredEvidenceBinding, ...],
    accepted_outcomes: tuple[EvidenceOutcome, ...],
    maximum_severity: SeverityLevel | None,
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...],
) -> OutcomePolicyDeclaration:
    return OutcomePolicyDeclaration(
        condition_id=ANALYSIS_POLICY_SATISFIED,
        required_bindings=required_bindings,
        accepted_outcomes=accepted_outcomes,
        minimum_numeric_value=None,
        maximum_numeric_value=None,
        maximum_severity=maximum_severity,
        maximum_failed_cases=None,
        replay_relevant_dependencies=replay_relevant_dependencies,
    )
