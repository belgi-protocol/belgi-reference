from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.edition import ExactEditionBinding
from belgi.profile.governance import ConditionId
from belgi.profile.reference_profile.identifiers.conditions import (
    REVIEW_POLICY_SATISFIED,
)

from .evidence import RequiredEvidenceBinding

__all__ = ["ReviewPolicyDeclaration", "review_policy_declaration"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewPolicyDeclaration:
    condition_id: ConditionId
    required_bindings: tuple[RequiredEvidenceBinding, ...]
    minimum_approvals: int
    allow_blocking_reviews: bool
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...]

    def __post_init__(self) -> None:
        if not self.required_bindings:
            raise ValueError("required_bindings must not be empty.")
        if self.minimum_approvals < 0:
            raise ValueError("minimum_approvals must be non-negative.")


def review_policy_declaration(
    *,
    required_bindings: tuple[RequiredEvidenceBinding, ...],
    minimum_approvals: int,
    allow_blocking_reviews: bool,
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...],
) -> ReviewPolicyDeclaration:
    return ReviewPolicyDeclaration(
        condition_id=REVIEW_POLICY_SATISFIED,
        required_bindings=required_bindings,
        minimum_approvals=minimum_approvals,
        allow_blocking_reviews=allow_blocking_reviews,
        replay_relevant_dependencies=replay_relevant_dependencies,
    )
