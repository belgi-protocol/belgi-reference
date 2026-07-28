from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Final, NewType

from belgi.carrier import CanonicalReference

from .instructions import (
    REPLAY_STEP_ORDER,
    STEP_LIFT_SEMANTIC_OBJECTS,
    STEP_READ_CLAIM_RECORD,
    STEP_VERIFY_CANONICAL_REFERENCE_UNIQUENESS,
    STEP_VERIFY_CLAIM_RECORD_INTEGRITY,
    STEP_VERIFY_CLAIM_RECORD_INTEGRITY_BINDING_PRESENCE,
    STEP_VERIFY_INTEGRITY_BINDING_PRESENCE,
    STEP_VERIFY_INTEGRITY_BINDINGS,
    STEP_VERIFY_PACKAGE_CLOSURE,
    STEP_VERIFY_REQUIRED_ROOT_MEMBERS,
    STEP_VERIFY_REQUIRED_ROOTS,
    ReplayStep,
)
from .outcome import (
    AMBIENT_CONTEXT_REQUIRED,
    INTEGRITY_FAILURE,
    LIFT_FAILURE,
    MALFORMED_CARRIER,
    NON_REPLAYABLE_CLAIM,
    UNRESOLVED_REFERENCE,
    ReplayOutcomeClass,
)

ReplayProblemType = NewType("ReplayProblemType", str)

MALFORMED_CLAIM_RECORD: Final[ReplayProblemType] = ReplayProblemType(
    "malformed-claim-record"
)
CLAIM_RECORD_INTEGRITY_BINDING_MISSING: Final[ReplayProblemType] = ReplayProblemType(
    "claim-record-integrity-binding-missing"
)
CLAIM_RECORD_INTEGRITY_BINDING_MISMATCH: Final[ReplayProblemType] = ReplayProblemType(
    "claim-record-integrity-binding-mismatch"
)
CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE: Final[ReplayProblemType] = ReplayProblemType(
    "claim-record-integrity-recovery-failure"
)
CLAIM_RECORD_INTEGRITY_RECOVERY_MALFORMED: Final[ReplayProblemType] = ReplayProblemType(
    "claim-record-integrity-recovery-malformed"
)
MISSING_REQUIRED_ROOT: Final[ReplayProblemType] = ReplayProblemType(
    "missing-required-root"
)
DUPLICATE_ROOT_DESIGNATION: Final[ReplayProblemType] = ReplayProblemType(
    "duplicate-root-designation"
)
MISSING_REQUIRED_MEMBER: Final[ReplayProblemType] = ReplayProblemType(
    "missing-required-member"
)
DUPLICATE_CANONICAL_REFERENCE: Final[ReplayProblemType] = ReplayProblemType(
    "duplicate-canonical-reference"
)
INTEGRITY_BINDING_MISSING: Final[ReplayProblemType] = ReplayProblemType(
    "integrity-binding-missing"
)
INTEGRITY_BINDING_MISMATCH: Final[ReplayProblemType] = ReplayProblemType(
    "integrity-binding-mismatch"
)
INTEGRITY_BINDING_SOURCE_FAILURE: Final[ReplayProblemType] = ReplayProblemType(
    "integrity-binding-source-failure"
)
OUT_OF_CLOSURE_DEPENDENCY: Final[ReplayProblemType] = ReplayProblemType(
    "out-of-closure-dependency"
)
UNRESOLVED_DEPENDENCY: Final[ReplayProblemType] = ReplayProblemType(
    "unresolved-dependency"
)
CARRIER_PARSE_FAILURE: Final[ReplayProblemType] = ReplayProblemType(
    "carrier-parse-failure"
)
CARRIER_RESOLVE_FAILURE: Final[ReplayProblemType] = ReplayProblemType(
    "carrier-resolve-failure"
)
INDUCE_FAILURE: Final[ReplayProblemType] = ReplayProblemType("induce-failure")
AMBIENT_CONTEXT_REQUIRED_PROBLEM: Final[ReplayProblemType] = ReplayProblemType(
    "ambient-context-required"
)
NON_DETERMINISTIC_LIFT: Final[ReplayProblemType] = ReplayProblemType(
    "non-deterministic-lift"
)
MINIMUM_REPLAY_PROBLEM_TYPES: Final[tuple[ReplayProblemType, ...]] = (
    MALFORMED_CLAIM_RECORD,
    CLAIM_RECORD_INTEGRITY_BINDING_MISSING,
    CLAIM_RECORD_INTEGRITY_BINDING_MISMATCH,
    CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
    CLAIM_RECORD_INTEGRITY_RECOVERY_MALFORMED,
    MISSING_REQUIRED_ROOT,
    DUPLICATE_ROOT_DESIGNATION,
    MISSING_REQUIRED_MEMBER,
    DUPLICATE_CANONICAL_REFERENCE,
    INTEGRITY_BINDING_MISSING,
    INTEGRITY_BINDING_SOURCE_FAILURE,
    INTEGRITY_BINDING_MISMATCH,
    OUT_OF_CLOSURE_DEPENDENCY,
    UNRESOLVED_DEPENDENCY,
    CARRIER_PARSE_FAILURE,
    CARRIER_RESOLVE_FAILURE,
    INDUCE_FAILURE,
    AMBIENT_CONTEXT_REQUIRED_PROBLEM,
    NON_DETERMINISTIC_LIFT,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplayProblem:
    type: ReplayProblemType
    title: str
    detail: str
    governing_step: ReplayStep
    related_reference: CanonicalReference | None = None
    procedure_substep: str | None = None

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("Replay problems require a non-empty title.")
        if not self.detail:
            raise ValueError("Replay problems require a non-empty detail.")


_PROBLEM_TO_OUTCOME: Final[dict[ReplayProblemType, ReplayOutcomeClass]] = {
    MALFORMED_CLAIM_RECORD: MALFORMED_CARRIER,
    CLAIM_RECORD_INTEGRITY_BINDING_MISSING: NON_REPLAYABLE_CLAIM,
    CLAIM_RECORD_INTEGRITY_BINDING_MISMATCH: INTEGRITY_FAILURE,
    CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE: INTEGRITY_FAILURE,
    CLAIM_RECORD_INTEGRITY_RECOVERY_MALFORMED: MALFORMED_CARRIER,
    MISSING_REQUIRED_ROOT: NON_REPLAYABLE_CLAIM,
    DUPLICATE_ROOT_DESIGNATION: NON_REPLAYABLE_CLAIM,
    MISSING_REQUIRED_MEMBER: NON_REPLAYABLE_CLAIM,
    DUPLICATE_CANONICAL_REFERENCE: NON_REPLAYABLE_CLAIM,
    INTEGRITY_BINDING_MISSING: NON_REPLAYABLE_CLAIM,
    INTEGRITY_BINDING_MISMATCH: INTEGRITY_FAILURE,
    INTEGRITY_BINDING_SOURCE_FAILURE: INTEGRITY_FAILURE,
    OUT_OF_CLOSURE_DEPENDENCY: NON_REPLAYABLE_CLAIM,
    UNRESOLVED_DEPENDENCY: UNRESOLVED_REFERENCE,
    CARRIER_PARSE_FAILURE: MALFORMED_CARRIER,
    CARRIER_RESOLVE_FAILURE: UNRESOLVED_REFERENCE,
    INDUCE_FAILURE: LIFT_FAILURE,
    AMBIENT_CONTEXT_REQUIRED_PROBLEM: AMBIENT_CONTEXT_REQUIRED,
    NON_DETERMINISTIC_LIFT: NON_REPLAYABLE_CLAIM,
}

_DEFAULT_GOVERNING_STEPS: Final[dict[ReplayProblemType, ReplayStep]] = {
    MALFORMED_CLAIM_RECORD: STEP_READ_CLAIM_RECORD,
    CLAIM_RECORD_INTEGRITY_BINDING_MISSING: STEP_VERIFY_CLAIM_RECORD_INTEGRITY_BINDING_PRESENCE,
    CLAIM_RECORD_INTEGRITY_BINDING_MISMATCH: STEP_VERIFY_CLAIM_RECORD_INTEGRITY,
    CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE: STEP_VERIFY_CLAIM_RECORD_INTEGRITY,
    CLAIM_RECORD_INTEGRITY_RECOVERY_MALFORMED: STEP_VERIFY_CLAIM_RECORD_INTEGRITY,
    MISSING_REQUIRED_ROOT: STEP_VERIFY_REQUIRED_ROOTS,
    DUPLICATE_ROOT_DESIGNATION: STEP_VERIFY_REQUIRED_ROOTS,
    MISSING_REQUIRED_MEMBER: STEP_VERIFY_REQUIRED_ROOT_MEMBERS,
    DUPLICATE_CANONICAL_REFERENCE: STEP_VERIFY_CANONICAL_REFERENCE_UNIQUENESS,
    OUT_OF_CLOSURE_DEPENDENCY: STEP_VERIFY_PACKAGE_CLOSURE,
    UNRESOLVED_DEPENDENCY: STEP_VERIFY_PACKAGE_CLOSURE,
    INTEGRITY_BINDING_MISSING: STEP_VERIFY_INTEGRITY_BINDING_PRESENCE,
    INTEGRITY_BINDING_MISMATCH: STEP_VERIFY_INTEGRITY_BINDINGS,
    INTEGRITY_BINDING_SOURCE_FAILURE: STEP_VERIFY_INTEGRITY_BINDINGS,
    CARRIER_PARSE_FAILURE: STEP_LIFT_SEMANTIC_OBJECTS,
    CARRIER_RESOLVE_FAILURE: STEP_LIFT_SEMANTIC_OBJECTS,
    INDUCE_FAILURE: STEP_LIFT_SEMANTIC_OBJECTS,
    NON_DETERMINISTIC_LIFT: STEP_LIFT_SEMANTIC_OBJECTS,
}

_STEP_INDEX: Final[dict[ReplayStep, int]] = {
    step: index for index, step in enumerate(REPLAY_STEP_ORDER)
}


def outcome_for_problem(*, problem_type: ReplayProblemType) -> ReplayOutcomeClass:
    try:
        return _PROBLEM_TO_OUTCOME[problem_type]
    except KeyError as exc:
        raise ValueError(f"Unknown replay problem type: {problem_type!r}") from exc


def default_step_for_problem(*, problem_type: ReplayProblemType) -> ReplayStep:
    if problem_type == AMBIENT_CONTEXT_REQUIRED_PROBLEM:
        raise ValueError(
            "ambient-context-required has no single default governing step; "
            "callers must set the actual step explicitly."
        )
    try:
        return _DEFAULT_GOVERNING_STEPS[problem_type]
    except KeyError as exc:
        raise ValueError(f"Unknown replay problem type: {problem_type!r}") from exc


def classify_outcome_from_problems(
    *, problems: Sequence[ReplayProblem]
) -> ReplayOutcomeClass:
    if not problems:
        raise ValueError(
            "At least one replay problem is required to classify a failure outcome."
        )

    chosen = problems[0]
    chosen_index = _STEP_INDEX[chosen.governing_step]
    for problem in problems[1:]:
        problem_index = _STEP_INDEX[problem.governing_step]
        if problem_index < chosen_index:
            chosen = problem
            chosen_index = problem_index
    return outcome_for_problem(problem_type=chosen.type)


def build_replay_problem(
    *,
    problem_type: ReplayProblemType,
    title: str,
    detail: str,
    governing_step: ReplayStep,
    related_reference: CanonicalReference | None = None,
    procedure_substep: str | None = None,
) -> ReplayProblem:
    return ReplayProblem(
        type=problem_type,
        title=title,
        detail=detail,
        governing_step=governing_step,
        related_reference=related_reference,
        procedure_substep=procedure_substep,
    )


__all__ = [
    "AMBIENT_CONTEXT_REQUIRED_PROBLEM",
    "CARRIER_PARSE_FAILURE",
    "CARRIER_RESOLVE_FAILURE",
    "CLAIM_RECORD_INTEGRITY_BINDING_MISMATCH",
    "CLAIM_RECORD_INTEGRITY_BINDING_MISSING",
    "CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE",
    "CLAIM_RECORD_INTEGRITY_RECOVERY_MALFORMED",
    "DUPLICATE_CANONICAL_REFERENCE",
    "DUPLICATE_ROOT_DESIGNATION",
    "INDUCE_FAILURE",
    "INTEGRITY_BINDING_MISMATCH",
    "INTEGRITY_BINDING_MISSING",
    "INTEGRITY_BINDING_SOURCE_FAILURE",
    "MALFORMED_CLAIM_RECORD",
    "MINIMUM_REPLAY_PROBLEM_TYPES",
    "MISSING_REQUIRED_MEMBER",
    "MISSING_REQUIRED_ROOT",
    "NON_DETERMINISTIC_LIFT",
    "OUT_OF_CLOSURE_DEPENDENCY",
    "UNRESOLVED_DEPENDENCY",
    "ReplayProblem",
    "ReplayProblemType",
    "build_replay_problem",
    "classify_outcome_from_problems",
    "default_step_for_problem",
    "outcome_for_problem",
]
