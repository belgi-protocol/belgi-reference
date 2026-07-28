from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.edition import ExactEditionBinding
from belgi.profile.governance import ConditionId
from belgi.profile.reference_profile.identifiers.conditions import (
    CHANGE_BASIS_RESOLVED,
)

__all__ = ["ChangeBasisDeclaration", "change_basis_declaration"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ChangeBasisDeclaration:
    condition_id: ConditionId
    require_proposal_identifier: bool
    require_baseline_identifier: bool
    require_proposal_source_state: bool
    require_baseline_source_state: bool
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...]


def change_basis_declaration(
    *,
    require_proposal_identifier: bool,
    require_baseline_identifier: bool,
    require_proposal_source_state: bool,
    require_baseline_source_state: bool,
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...],
) -> ChangeBasisDeclaration:
    return ChangeBasisDeclaration(
        condition_id=CHANGE_BASIS_RESOLVED,
        require_proposal_identifier=require_proposal_identifier,
        require_baseline_identifier=require_baseline_identifier,
        require_proposal_source_state=require_proposal_source_state,
        require_baseline_source_state=require_baseline_source_state,
        replay_relevant_dependencies=replay_relevant_dependencies,
    )
