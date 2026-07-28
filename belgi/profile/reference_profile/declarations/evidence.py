from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from belgi.profile.edition import ExactEditionBinding
from belgi.profile.governance import (
    AuthorityLevelId,
    BindingKindId,
    ConditionId,
    EvidenceKindId,
    EvidenceSourceClassId,
)
from belgi.profile.reference_profile.identifiers.binding_kinds import SATISFIES
from belgi.profile.reference_profile.identifiers.conditions import (
    REQUIRED_EVIDENCE_PRESENT,
)

__all__ = [
    "EvidenceOutcome",
    "EvidencePresenceDeclaration",
    "RequiredEvidenceBinding",
    "evidence_presence_declaration",
]


class EvidenceOutcome(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"
    BLOCK = "block"


@dataclass(frozen=True, slots=True, kw_only=True)
class RequiredEvidenceBinding:
    evidence_kind: EvidenceKindId
    binding_kind: BindingKindId
    minimum_count: int
    minimum_authority: AuthorityLevelId
    allowed_source_classes: tuple[EvidenceSourceClassId, ...]
    exact_evidence_identifiers: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.minimum_count < 1:
            raise ValueError("minimum_count must be at least 1.")
        if self.binding_kind != SATISFIES:
            raise ValueError(
                "reference-profile condition declarations require "
                "belgi.software-change.binding.satisfies; non-decisive or "
                "refuting binding kinds remain descriptive carrier material "
                "outside evaluator semantics."
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidencePresenceDeclaration:
    condition_id: ConditionId
    required_bindings: tuple[RequiredEvidenceBinding, ...]
    require_interpretable_bindings: bool
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...]

    def __post_init__(self) -> None:
        if not self.required_bindings:
            raise ValueError("required_bindings must not be empty.")


def evidence_presence_declaration(
    *,
    required_bindings: tuple[RequiredEvidenceBinding, ...],
    require_interpretable_bindings: bool,
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...],
) -> EvidencePresenceDeclaration:
    return EvidencePresenceDeclaration(
        condition_id=REQUIRED_EVIDENCE_PRESENT,
        required_bindings=required_bindings,
        require_interpretable_bindings=require_interpretable_bindings,
        replay_relevant_dependencies=replay_relevant_dependencies,
    )
