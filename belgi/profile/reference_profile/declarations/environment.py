from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.edition import ExactEditionBinding
from belgi.profile.governance import (
    ConditionId,
    EnvironmentTermId,
    ReplayPolicyId,
    ToolchainSetId,
)
from belgi.profile.reference_profile.identifiers.conditions import (
    ENVIRONMENT_COMPATIBILITY_SATISFIED,
)

from .evidence import RequiredEvidenceBinding

__all__ = [
    "EnvironmentCompatibilityDeclaration",
    "EnvironmentRequirement",
    "EnvironmentTermValue",
    "environment_compatibility_declaration",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class EnvironmentTermValue:
    term_id: EnvironmentTermId
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("environment term value must not be empty.")


@dataclass(frozen=True, slots=True, kw_only=True)
class EnvironmentRequirement:
    term_id: EnvironmentTermId
    accepted_values: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.accepted_values:
            raise ValueError("accepted_values must not be empty.")


@dataclass(frozen=True, slots=True, kw_only=True)
class EnvironmentCompatibilityDeclaration:
    condition_id: ConditionId
    required_bindings: tuple[RequiredEvidenceBinding, ...]
    required_terms: tuple[EnvironmentRequirement, ...]
    accepted_toolchain_sets: tuple[ToolchainSetId, ...]
    equivalence_basis_identifiers: tuple[str, ...]
    replay_policy: ReplayPolicyId
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...]

    def __post_init__(self) -> None:
        if not self.required_bindings:
            raise ValueError("required_bindings must not be empty.")
        if not self.required_terms:
            raise ValueError("required_terms must not be empty.")


def environment_compatibility_declaration(
    *,
    required_bindings: tuple[RequiredEvidenceBinding, ...],
    required_terms: tuple[EnvironmentRequirement, ...],
    accepted_toolchain_sets: tuple[ToolchainSetId, ...],
    equivalence_basis_identifiers: tuple[str, ...],
    replay_policy: ReplayPolicyId,
    replay_relevant_dependencies: tuple[ExactEditionBinding, ...],
) -> EnvironmentCompatibilityDeclaration:
    return EnvironmentCompatibilityDeclaration(
        condition_id=ENVIRONMENT_COMPATIBILITY_SATISFIED,
        required_bindings=required_bindings,
        required_terms=required_terms,
        accepted_toolchain_sets=accepted_toolchain_sets,
        equivalence_basis_identifiers=equivalence_basis_identifiers,
        replay_policy=replay_policy,
        replay_relevant_dependencies=replay_relevant_dependencies,
    )
