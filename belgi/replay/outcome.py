from __future__ import annotations

from typing import Final, NewType

ReplayStatus = NewType("ReplayStatus", str)
ReplayOutcomeClass = NewType("ReplayOutcomeClass", str)

REPLAYABLE: Final[ReplayStatus] = ReplayStatus("replayable")
NON_REPLAYABLE: Final[ReplayStatus] = ReplayStatus("non-replayable")

SUCCESSFUL_REPLAY: Final[ReplayOutcomeClass] = ReplayOutcomeClass("successful-replay")
MALFORMED_CARRIER: Final[ReplayOutcomeClass] = ReplayOutcomeClass("malformed-carrier")
UNRESOLVED_REFERENCE: Final[ReplayOutcomeClass] = ReplayOutcomeClass(
    "unresolved-reference"
)
INTEGRITY_FAILURE: Final[ReplayOutcomeClass] = ReplayOutcomeClass("integrity-failure")
LIFT_FAILURE: Final[ReplayOutcomeClass] = ReplayOutcomeClass("lift-failure")
AMBIENT_CONTEXT_REQUIRED: Final[ReplayOutcomeClass] = ReplayOutcomeClass(
    "ambient-context-required"
)
NON_REPLAYABLE_CLAIM: Final[ReplayOutcomeClass] = ReplayOutcomeClass(
    "non-replayable-claim"
)

MINIMUM_REPLAY_OUTCOME_CLASSES: Final[tuple[ReplayOutcomeClass, ...]] = (
    SUCCESSFUL_REPLAY,
    MALFORMED_CARRIER,
    UNRESOLVED_REFERENCE,
    INTEGRITY_FAILURE,
    LIFT_FAILURE,
    AMBIENT_CONTEXT_REQUIRED,
    NON_REPLAYABLE_CLAIM,
)

_SUCCESSFUL_OUTCOMES: Final[frozenset[ReplayOutcomeClass]] = frozenset(
    {SUCCESSFUL_REPLAY}
)
_FAILURE_OUTCOMES: Final[frozenset[ReplayOutcomeClass]] = frozenset(
    {
        MALFORMED_CARRIER,
        UNRESOLVED_REFERENCE,
        INTEGRITY_FAILURE,
        LIFT_FAILURE,
        AMBIENT_CONTEXT_REQUIRED,
        NON_REPLAYABLE_CLAIM,
    }
)


def status_for_outcome(*, outcome_class: ReplayOutcomeClass) -> ReplayStatus:
    if outcome_class in _SUCCESSFUL_OUTCOMES:
        return REPLAYABLE
    if outcome_class in _FAILURE_OUTCOMES:
        return NON_REPLAYABLE
    raise ValueError(f"Unknown replay outcome class: {outcome_class!r}")


def is_successful_outcome(*, outcome_class: ReplayOutcomeClass) -> bool:
    return outcome_class in _SUCCESSFUL_OUTCOMES


__all__ = [
    "AMBIENT_CONTEXT_REQUIRED",
    "INTEGRITY_FAILURE",
    "LIFT_FAILURE",
    "MALFORMED_CARRIER",
    "MINIMUM_REPLAY_OUTCOME_CLASSES",
    "NON_REPLAYABLE",
    "NON_REPLAYABLE_CLAIM",
    "REPLAYABLE",
    "SUCCESSFUL_REPLAY",
    "UNRESOLVED_REFERENCE",
    "ReplayOutcomeClass",
    "ReplayStatus",
    "is_successful_outcome",
    "status_for_outcome",
]
