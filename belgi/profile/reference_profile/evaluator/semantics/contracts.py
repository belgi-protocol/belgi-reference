from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from belgi.core import SemanticsKey
from belgi.profile.edition import ImmutableDesignator
from belgi.profile.governance import ConditionId

__all__ = [
    "ConditionSemanticsBinding",
    "ProfileSatFunction",
    "SemanticsProviderWitness",
]


class ProfileSatFunction(Protocol):
    """Profile-owned semantics over semantic objects and a declared condition."""

    def __call__(
        self,
        judged_object: object,
        evidence_state: object,
        condition: object,
    ) -> bool: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class ConditionSemanticsBinding:
    condition_id: ConditionId
    semantics_key: SemanticsKey
    implementation: ProfileSatFunction


@dataclass(frozen=True, slots=True, kw_only=True)
class SemanticsProviderWitness:
    semantics_key: SemanticsKey
    source_designator: ImmutableDesignator
    provider_identifier: str
    callable_entrypoint: str
