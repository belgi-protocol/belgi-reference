from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NewType

from .edition import EditionKind, ExactEdition, ExactEditionBinding
from .exceptions import (
    GovernanceError as _GovernanceError,
)
from .exceptions import (
    ProtectedCoreViolationError as _ProtectedCoreViolationError,
)
from .exceptions import (
    UndeclaredExtensionPointError as _UndeclaredExtensionPointError,
)
from .extension_points import (
    ALL_RESERVED_EXTENSION_POINTS,
    ReservedExtensionPoint,
    normalize_extension_points,
)

__all__ = [
    "DEFAULT_GOVERNANCE_ENGINE",
    "AuthorityLevelId",
    "BindingKindId",
    "BoundaryParticipationId",
    "CompanionSpecification",
    "ConditionId",
    "ConformanceRequirementId",
    "DeclarationSurface",
    "DependencyReference",
    "EnvironmentTermId",
    "EvaluatorParameterId",
    "EvidenceKindId",
    "EvidenceSourceClassId",
    "FailureId",
    "GovernanceEngine",
    "GovernanceReview",
    "ProfileSpecification",
    "ProhibitedRedefinition",
    "ReplayPolicyId",
    "SpecificationKind",
    "ToolchainSetId",
    "review_companion_specification",
    "review_profile_specification",
    "validate_companion_specification",
    "validate_profile_specification",
]


ConditionId = NewType("ConditionId", str)
EvidenceKindId = NewType("EvidenceKindId", str)
EvidenceSourceClassId = NewType("EvidenceSourceClassId", str)
BoundaryParticipationId = NewType("BoundaryParticipationId", str)
AuthorityLevelId = NewType("AuthorityLevelId", str)
BindingKindId = NewType("BindingKindId", str)
ReplayPolicyId = NewType("ReplayPolicyId", str)
EnvironmentTermId = NewType("EnvironmentTermId", str)
EvaluatorParameterId = NewType("EvaluatorParameterId", str)
FailureId = NewType("FailureId", str)
ToolchainSetId = NewType("ToolchainSetId", str)
ConformanceRequirementId = NewType("ConformanceRequirementId", str)


class SpecificationKind(str, Enum):
    PROFILE = "profile"
    COMPANION = "companion"


class ProhibitedRedefinition(str, Enum):
    NEW_SEMANTIC_SORT = "new-semantic-sort"
    NEW_VERDICT_VALUE = "new-verdict-value"
    EXTENSIONAL_EVALUATOR_IDENTITY = "extensional-evaluator-identity"
    CLAIM_IDENTITY = "claim-identity"
    REPLAYABLE_CLAIM = "replayable-claim"
    REQUIRED_CARRIER_ROLE = "required-carrier-role"
    REQUIRED_LIFTING_STAGE = "required-lifting-stage"
    REPLAY_PACKAGE_CLOSURE = "replay-package-closure"
    INTEGRITY_VERIFICATION = "integrity-verification"
    MINIMUM_REPLAY_OUTCOME_CLASSES = "minimum-replay-outcome-classes"
    MINIMUM_REPLAY_PROBLEM_TYPES = "minimum-replay-problem-types"
    HIDDEN_DEFAULT_PROFILE_SELECTION = "hidden-default-profile-selection"
    UNDECLARED_AMBIENT_CONTEXT = "undeclared-ambient-context"


@dataclass(frozen=True, slots=True, kw_only=True)
class DependencyReference:
    binding: ExactEditionBinding
    replay_relevant: bool
    clause_locator: str

    def __post_init__(self) -> None:
        if not self.clause_locator:
            raise _GovernanceError("clause_locator must not be empty.")


@dataclass(frozen=True, slots=True, kw_only=True)
class DeclarationSurface:
    identifier: str
    extension_point: ReservedExtensionPoint
    mandatory: bool

    def __post_init__(self) -> None:
        if not self.identifier:
            raise _GovernanceError("declaration surface identifier must not be empty.")


@dataclass(frozen=True, slots=True, kw_only=True)
class ProfileSpecification:
    edition: ExactEdition
    belgi_dependencies: tuple[ExactEditionBinding, ...]
    selected_companions: tuple[ExactEditionBinding, ...]
    used_extension_points: tuple[ReservedExtensionPoint, ...]
    declarations: tuple[DeclarationSurface, ...]
    conformance_requirements: tuple[ConformanceRequirementId, ...]
    exact_dependencies: tuple[DependencyReference, ...]
    prohibited_redefinitions: frozenset[ProhibitedRedefinition]

    def __post_init__(self) -> None:
        if self.edition.kind != EditionKind.PROFILE:
            raise _GovernanceError(
                "profile specification requires a profile exact edition."
            )
        if not self.belgi_dependencies:
            raise _GovernanceError(
                "profile specification must declare BELGI dependencies."
            )
        if not self.conformance_requirements:
            raise _GovernanceError(
                "profile specification must publish conformance requirements."
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class CompanionSpecification:
    edition: ExactEdition
    served_extension_points: tuple[ReservedExtensionPoint, ...]
    declarations: tuple[DeclarationSurface, ...]
    conformance_requirements: tuple[ConformanceRequirementId, ...]
    exact_dependencies: tuple[DependencyReference, ...]
    prohibited_redefinitions: frozenset[ProhibitedRedefinition]

    def __post_init__(self) -> None:
        if self.edition.kind != EditionKind.COMPANION:
            raise _GovernanceError(
                "companion specification requires a companion exact edition."
            )
        if not self.conformance_requirements:
            raise _GovernanceError(
                "companion specification must publish conformance requirements."
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class GovernanceReview:
    kind: SpecificationKind
    valid: bool
    normalized_extension_points: tuple[ReservedExtensionPoint, ...]
    prohibited_redefinitions: tuple[ProhibitedRedefinition, ...]
    replay_relevant_dependencies: tuple[DependencyReference, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class GovernanceEngine:
    reserved_extension_points: tuple[ReservedExtensionPoint, ...]

    def review_profile(
        self,
        *,
        specification: ProfileSpecification,
    ) -> GovernanceReview:
        normalized_points = self._normalize_points(
            points=specification.used_extension_points
        )
        self._assert_no_protected_core_violation(
            prohibited_redefinitions=specification.prohibited_redefinitions
        )
        self._assert_profile_companion_bindings(
            selected_companions=specification.selected_companions
        )
        return GovernanceReview(
            kind=SpecificationKind.PROFILE,
            valid=True,
            normalized_extension_points=normalized_points,
            prohibited_redefinitions=tuple(specification.prohibited_redefinitions),
            replay_relevant_dependencies=tuple(
                dependency
                for dependency in specification.exact_dependencies
                if dependency.replay_relevant
            ),
        )

    def review_companion(
        self,
        *,
        specification: CompanionSpecification,
    ) -> GovernanceReview:
        normalized_points = self._normalize_points(
            points=specification.served_extension_points
        )
        self._assert_no_protected_core_violation(
            prohibited_redefinitions=specification.prohibited_redefinitions
        )
        return GovernanceReview(
            kind=SpecificationKind.COMPANION,
            valid=True,
            normalized_extension_points=normalized_points,
            prohibited_redefinitions=tuple(specification.prohibited_redefinitions),
            replay_relevant_dependencies=tuple(
                dependency
                for dependency in specification.exact_dependencies
                if dependency.replay_relevant
            ),
        )

    def validate_profile(
        self,
        *,
        specification: ProfileSpecification,
    ) -> None:
        self.review_profile(specification=specification)

    def validate_companion(
        self,
        *,
        specification: CompanionSpecification,
    ) -> None:
        self.review_companion(specification=specification)

    def _normalize_points(
        self,
        *,
        points: tuple[ReservedExtensionPoint, ...],
    ) -> tuple[ReservedExtensionPoint, ...]:
        normalized = normalize_extension_points(points=points)
        unexpected = tuple(
            point for point in normalized if point not in self.reserved_extension_points
        )
        if unexpected:
            raise _UndeclaredExtensionPointError(
                "undeclared reserved extension points: "
                + ", ".join(f"{point.clause} ({point.title})" for point in unexpected)
            )
        return normalized

    @staticmethod
    def _assert_no_protected_core_violation(
        *,
        prohibited_redefinitions: frozenset[ProhibitedRedefinition],
    ) -> None:
        if prohibited_redefinitions:
            identifiers = ", ".join(
                sorted(item.value for item in prohibited_redefinitions)
            )
            raise _ProtectedCoreViolationError(
                f"protected BELGI meaning cannot be reopened: {identifiers}."
            )

    @staticmethod
    def _assert_profile_companion_bindings(
        *,
        selected_companions: tuple[ExactEditionBinding, ...],
    ) -> None:
        for binding in selected_companions:
            if binding.kind != EditionKind.COMPANION:
                raise _GovernanceError(
                    "selected_companions must contain companion exact-edition bindings only."
                )


DEFAULT_GOVERNANCE_ENGINE = GovernanceEngine(
    reserved_extension_points=ALL_RESERVED_EXTENSION_POINTS
)


def review_profile_specification(
    *,
    specification: ProfileSpecification,
) -> GovernanceReview:
    return DEFAULT_GOVERNANCE_ENGINE.review_profile(specification=specification)


def review_companion_specification(
    *,
    specification: CompanionSpecification,
) -> GovernanceReview:
    return DEFAULT_GOVERNANCE_ENGINE.review_companion(specification=specification)


def validate_profile_specification(
    *,
    specification: ProfileSpecification,
) -> None:
    DEFAULT_GOVERNANCE_ENGINE.validate_profile(specification=specification)


def validate_companion_specification(
    *,
    specification: CompanionSpecification,
) -> None:
    DEFAULT_GOVERNANCE_ENGINE.validate_companion(specification=specification)
