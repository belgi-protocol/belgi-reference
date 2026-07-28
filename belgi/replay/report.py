from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Generic, NewType, TypeVar

from belgi.carrier import PackageIdentifier

from .instructions import REPLAY_STEP_ORDER, STEP_READ_CLAIM_RECORD
from .outcome import (
    NON_REPLAYABLE,
    REPLAYABLE,
    SUCCESSFUL_REPLAY,
    ReplayOutcomeClass,
    ReplayStatus,
    is_successful_outcome,
    status_for_outcome,
)
from .problems import (
    MALFORMED_CLAIM_RECORD,
    ReplayProblem,
    classify_outcome_from_problems,
)

__all__ = [
    "CACHED_VERDICT_MISMATCH",
    "REPLAY_REPORT_EXACT_FIELD_EQUALITY_RULE",
    "REPLAY_REPORT_FIELD_COMPARISON_EXCLUDED_FIELDS",
    "REPLAY_REPORT_FIELD_COMPARISON_INCLUDED_FIELDS",
    "REPLAY_REPORT_FIELD_COMPARISON_SEQUENCE_SEMANTICS",
    "REPLAY_REPORT_FIELD_PROJECTIONS",
    "REPLAY_REPORT_JSON_ENCODING",
    "REPLAY_REPORT_OUTPUT_SURFACE",
    "REPLAY_REPORT_SCHEMA_NAME",
    "ReplayReport",
    "ReplayWarning",
    "ReplayWarningType",
    "failed_report",
    "successful_report",
]


ReplayWarningType = NewType("ReplayWarningType", str)
CACHED_VERDICT_MISMATCH = ReplayWarningType("cached-verdict-mismatch")
REPLAY_REPORT_OUTPUT_SURFACE = "replay-report"
REPLAY_REPORT_JSON_ENCODING = "carrier-replay-report-json"
REPLAY_REPORT_EXACT_FIELD_EQUALITY_RULE = "exact-report-field-equality"
REPLAY_REPORT_SCHEMA_NAME = "ReplayReport.schema.json"
REPLAY_REPORT_FIELD_PROJECTIONS = {
    "status": "status",
    "outcome_class": "outcomeClass",
    "package_identifier": "packageIdentifier",
    "derived_verdict": "derivedVerdict",
    "problem_types": "problems[].type",
    "warning_types": "warnings[].type",
}
REPLAY_REPORT_FIELD_COMPARISON_INCLUDED_FIELDS = tuple(
    REPLAY_REPORT_FIELD_PROJECTIONS[field_name]
    for field_name in (
        "status",
        "outcome_class",
        "package_identifier",
        "derived_verdict",
        "problem_types",
        "warning_types",
    )
)
REPLAY_REPORT_FIELD_COMPARISON_EXCLUDED_FIELDS = (
    "problems[].title",
    "problems[].detail",
    "problems[].relatedReference",
    "warnings[].title",
    "warnings[].detail",
    "warnings[].relatedReference",
)
REPLAY_REPORT_FIELD_COMPARISON_SEQUENCE_SEMANTICS = "ordered"

VerdictT = TypeVar("VerdictT")


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplayWarning:
    type: ReplayWarningType
    title: str
    detail: str

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("Replay warnings require a non-empty title.")
        if not self.detail:
            raise ValueError("Replay warnings require a non-empty detail.")


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplayReport(Generic[VerdictT]):
    status: ReplayStatus
    outcome_class: ReplayOutcomeClass
    package_identifier: PackageIdentifier | None
    problems: tuple[ReplayProblem, ...]
    warnings: tuple[ReplayWarning, ...]
    derived_verdict: VerdictT | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "problems", tuple(self.problems))
        object.__setattr__(self, "warnings", tuple(self.warnings))
        if self.package_identifier is None:
            primary_problem = (
                None if not self.problems else _primary_problem(self.problems)
            )
            if (
                self.status != NON_REPLAYABLE
                or primary_problem is None
                or primary_problem.governing_step != STEP_READ_CLAIM_RECORD
                or primary_problem.type != MALFORMED_CLAIM_RECORD
            ):
                raise ValueError(
                    "Replay report package identifier may be unavailable only for "
                    "a primary malformed-claim-record step-1 failure."
                )
        elif (
            not isinstance(self.package_identifier, str)
            or self.package_identifier == ""
        ):
            raise ValueError(
                "Replay report package identifier must be a non-empty string."
            )
        if is_successful_outcome(outcome_class=self.outcome_class):
            if self.status != REPLAYABLE:
                raise ValueError(
                    "Successful replay reports must have replayable status."
                )
            if self.outcome_class != SUCCESSFUL_REPLAY:
                raise ValueError(
                    "Replayable status requires the successful-replay outcome class."
                )
            if self.problems:
                raise ValueError(
                    "Successful replay reports must not include replay problems."
                )
            if self.derived_verdict is None:
                raise ValueError("Successful replay reports require a derived verdict.")
            return

        if self.status != NON_REPLAYABLE:
            raise ValueError("Failed replay reports must have non-replayable status.")
        if not self.problems:
            raise ValueError(
                "Failed replay reports require at least one replay problem."
            )
        if self.derived_verdict is not None:
            raise ValueError("Failed replay reports must not carry a derived verdict.")

    @classmethod
    def successful(
        cls,
        *,
        package_identifier: PackageIdentifier,
        derived_verdict: VerdictT,
        warnings: Sequence[ReplayWarning] = (),
    ) -> ReplayReport[VerdictT]:
        return cls(
            status=REPLAYABLE,
            outcome_class=SUCCESSFUL_REPLAY,
            package_identifier=package_identifier,
            problems=(),
            warnings=tuple(warnings),
            derived_verdict=derived_verdict,
        )

    @classmethod
    def failure(
        cls,
        *,
        package_identifier: PackageIdentifier | None,
        problems: Sequence[ReplayProblem],
        warnings: Sequence[ReplayWarning] = (),
    ) -> ReplayReport[VerdictT]:
        if not problems:
            raise ValueError(
                "Replay failure reports require at least one replay problem."
            )
        outcome_class = classify_outcome_from_problems(problems=tuple(problems))
        return cls(
            status=status_for_outcome(outcome_class=outcome_class),
            outcome_class=outcome_class,
            package_identifier=package_identifier,
            problems=tuple(problems),
            warnings=tuple(warnings),
        )


def successful_report(
    *,
    package_identifier: PackageIdentifier,
    derived_verdict: VerdictT,
    warnings: Sequence[ReplayWarning] = (),
) -> ReplayReport[VerdictT]:
    return ReplayReport.successful(
        package_identifier=package_identifier,
        derived_verdict=derived_verdict,
        warnings=warnings,
    )


def failed_report(
    *,
    package_identifier: PackageIdentifier | None,
    problems: Sequence[ReplayProblem],
    warnings: Sequence[ReplayWarning] = (),
) -> ReplayReport[Any]:
    return ReplayReport.failure(
        package_identifier=package_identifier,
        problems=problems,
        warnings=warnings,
    )


def _primary_problem(problems: tuple[ReplayProblem, ...]) -> ReplayProblem:
    return min(
        problems,
        key=lambda problem: REPLAY_STEP_ORDER.index(problem.governing_step),
    )
