from __future__ import annotations

from dataclasses import dataclass
from typing import Final, NewType

ReplayStep = NewType("ReplayStep", str)

STEP_READ_CLAIM_RECORD: Final[ReplayStep] = ReplayStep("step-1-read-claim-record")
STEP_VERIFY_CLAIM_RECORD_INTEGRITY_BINDING_PRESENCE: Final[ReplayStep] = ReplayStep(
    "step-2-verify-claim-record-integrity-binding-presence"
)
STEP_VERIFY_CLAIM_RECORD_INTEGRITY: Final[ReplayStep] = ReplayStep(
    "step-3-verify-claim-record-integrity"
)
STEP_VALIDATE_AUTHENTICATED_CLAIM_RECORD: Final[ReplayStep] = ReplayStep(
    "step-4-validate-authenticated-claim-record"
)
STEP_VERIFY_REQUIRED_ROOTS: Final[ReplayStep] = ReplayStep(
    "step-5-verify-required-roots"
)
STEP_VERIFY_REQUIRED_ROOT_MEMBERS: Final[ReplayStep] = ReplayStep(
    "step-6-verify-required-root-members"
)
STEP_VERIFY_CANONICAL_REFERENCE_UNIQUENESS: Final[ReplayStep] = ReplayStep(
    "step-7-verify-canonical-reference-uniqueness"
)
STEP_VERIFY_PACKAGE_CLOSURE: Final[ReplayStep] = ReplayStep(
    "step-8-verify-package-closure"
)
STEP_VERIFY_INTEGRITY_BINDING_PRESENCE: Final[ReplayStep] = ReplayStep(
    "step-9-verify-integrity-binding-presence"
)
STEP_VERIFY_INTEGRITY_BINDINGS: Final[ReplayStep] = ReplayStep(
    "step-10-verify-integrity-bindings"
)
STEP_LIFT_SEMANTIC_OBJECTS: Final[ReplayStep] = ReplayStep(
    "step-11-lift-semantic-objects"
)
STEP_DERIVE_VERDICT: Final[ReplayStep] = ReplayStep("step-12-derive-verdict")
STEP_CLASSIFY_RESULT: Final[ReplayStep] = ReplayStep("step-13-classify-result")
STEP_EMIT_REPORT: Final[ReplayStep] = ReplayStep("step-14-emit-report")

REPLAY_STEP_ORDER: Final[tuple[ReplayStep, ...]] = (
    STEP_READ_CLAIM_RECORD,
    STEP_VERIFY_CLAIM_RECORD_INTEGRITY_BINDING_PRESENCE,
    STEP_VERIFY_CLAIM_RECORD_INTEGRITY,
    STEP_VALIDATE_AUTHENTICATED_CLAIM_RECORD,
    STEP_VERIFY_REQUIRED_ROOTS,
    STEP_VERIFY_REQUIRED_ROOT_MEMBERS,
    STEP_VERIFY_CANONICAL_REFERENCE_UNIQUENESS,
    STEP_VERIFY_PACKAGE_CLOSURE,
    STEP_VERIFY_INTEGRITY_BINDING_PRESENCE,
    STEP_VERIFY_INTEGRITY_BINDINGS,
    STEP_LIFT_SEMANTIC_OBJECTS,
    STEP_DERIVE_VERDICT,
    STEP_CLASSIFY_RESULT,
    STEP_EMIT_REPORT,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplayInstructions:
    repeatability_checks: int = 2

    def __post_init__(self) -> None:
        if self.repeatability_checks < 2:
            raise ValueError("repeatability_checks must be at least 2.")


STANDARD_REPLAY_INSTRUCTIONS: Final[ReplayInstructions] = ReplayInstructions(
    repeatability_checks=2
)


__all__ = [
    "REPLAY_STEP_ORDER",
    "STANDARD_REPLAY_INSTRUCTIONS",
    "STEP_CLASSIFY_RESULT",
    "STEP_DERIVE_VERDICT",
    "STEP_EMIT_REPORT",
    "STEP_LIFT_SEMANTIC_OBJECTS",
    "STEP_READ_CLAIM_RECORD",
    "STEP_VALIDATE_AUTHENTICATED_CLAIM_RECORD",
    "STEP_VERIFY_CANONICAL_REFERENCE_UNIQUENESS",
    "STEP_VERIFY_CLAIM_RECORD_INTEGRITY",
    "STEP_VERIFY_CLAIM_RECORD_INTEGRITY_BINDING_PRESENCE",
    "STEP_VERIFY_INTEGRITY_BINDINGS",
    "STEP_VERIFY_INTEGRITY_BINDING_PRESENCE",
    "STEP_VERIFY_PACKAGE_CLOSURE",
    "STEP_VERIFY_REQUIRED_ROOTS",
    "STEP_VERIFY_REQUIRED_ROOT_MEMBERS",
    "ReplayInstructions",
    "ReplayStep",
]
