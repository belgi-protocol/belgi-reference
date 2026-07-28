from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.governance import FailureId

__all__ = [
    "ALL_FAILURES",
    "ENVIRONMENT_DRIFT",
    "EXCLUDED_SOURCE_RELIANCE",
    "INVALID_EDITION_BINDING",
    "MISSING_REQUIRED_BINDING",
    "MISSING_REQUIRED_DECLARATION",
    "MISSING_REQUIRED_PARAMETER",
    "PROTECTED_CORE_VIOLATION",
    "UNRESOLVED_REPLAY_DEPENDENCY",
    "FailureTerm",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class FailureTerm:
    identifier: FailureId
    title: str
    description: str


MISSING_REQUIRED_DECLARATION = FailureTerm(
    identifier=FailureId("belgi.profile.failure.missing-required-declaration"),
    title="Missing required declaration",
    description="Replay-relevant declaration material was absent.",
)
MISSING_REQUIRED_BINDING = FailureTerm(
    identifier=FailureId("belgi.profile.failure.missing-required-binding"),
    title="Missing required binding",
    description="A required condition lacked an applicable evidence binding.",
)
MISSING_REQUIRED_PARAMETER = FailureTerm(
    identifier=FailureId("belgi.profile.failure.missing-required-parameter"),
    title="Missing required parameter",
    description="A replay-relevant evaluator parameter was absent.",
)
UNRESOLVED_REPLAY_DEPENDENCY = FailureTerm(
    identifier=FailureId("belgi.profile.failure.unresolved-replay-dependency"),
    title="Unresolved replay dependency",
    description="A replay-relevant exact-edition dependency could not be resolved.",
)
EXCLUDED_SOURCE_RELIANCE = FailureTerm(
    identifier=FailureId("belgi.profile.failure.excluded-source-reliance"),
    title="Excluded source reliance",
    description="Excluded material or included non-authoritative evidence was treated as decisive.",
)
ENVIRONMENT_DRIFT = FailureTerm(
    identifier=FailureId("belgi.profile.failure.environment-drift"),
    title="Environment drift",
    description="Replay-relevant environment identity diverged without declared equivalence.",
)
INVALID_EDITION_BINDING = FailureTerm(
    identifier=FailureId("belgi.profile.failure.invalid-edition-binding"),
    title="Invalid edition binding",
    description="Exact-edition identity was malformed, ambiguous, or floating.",
)
PROTECTED_CORE_VIOLATION = FailureTerm(
    identifier=FailureId("belgi.profile.failure.protected-core-violation"),
    title="Protected core violation",
    description="A profile or companion tried to redefine protected BELGI semantics.",
)

ALL_FAILURES: tuple[FailureTerm, ...] = (
    MISSING_REQUIRED_DECLARATION,
    MISSING_REQUIRED_BINDING,
    MISSING_REQUIRED_PARAMETER,
    UNRESOLVED_REPLAY_DEPENDENCY,
    EXCLUDED_SOURCE_RELIANCE,
    ENVIRONMENT_DRIFT,
    INVALID_EDITION_BINDING,
    PROTECTED_CORE_VIOLATION,
)
