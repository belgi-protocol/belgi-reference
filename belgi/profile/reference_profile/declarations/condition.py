from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from belgi.core import (
    Condition,
    ResolvedConditionSemantics,
    SemanticsKey,
)
from belgi.core import (
    ConditionId as CoreConditionId,
)

from .change_basis import ChangeBasisDeclaration
from .environment import EnvironmentCompatibilityDeclaration
from .evidence import EvidencePresenceDeclaration
from .outcome import OutcomePolicyDeclaration
from .review import ReviewPolicyDeclaration

__all__ = [
    "ProfileCondition",
    "ProfileConditionDeclaration",
    "declared_profile_condition",
]


ProfileConditionDeclaration: TypeAlias = (
    ChangeBasisDeclaration
    | EvidencePresenceDeclaration
    | OutcomePolicyDeclaration
    | ReviewPolicyDeclaration
    | EnvironmentCompatibilityDeclaration
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileCondition(Condition):
    """Core Condition plus the profile declaration consumed by profile semantics."""

    profile_declaration: ProfileConditionDeclaration

    def __post_init__(self) -> None:
        Condition.__post_init__(self)
        if str(self.profile_declaration.condition_id) != str(self.condition_id):
            raise ValueError(
                "profile_declaration.condition_id must match condition_id."
            )


def declared_profile_condition(
    *,
    declaration: ProfileConditionDeclaration,
    semantics_key: SemanticsKey | None = None,
) -> ProfileCondition:
    condition_id = CoreConditionId(str(declaration.condition_id))
    return ProfileCondition(
        condition_id=condition_id,
        determining_semantics=ResolvedConditionSemantics(
            semantics_key=semantics_key or SemanticsKey(str(declaration.condition_id))
        ),
        profile_declaration=declaration,
    )
