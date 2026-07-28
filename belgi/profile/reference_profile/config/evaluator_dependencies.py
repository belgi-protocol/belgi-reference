from __future__ import annotations

from belgi.profile.edition import ExactEditionBinding, ImmutableDesignator
from belgi.profile.reference_profile.declarations import (
    CI_EXECUTION_SOURCE,
    DEVELOPER_WORKSPACE_SOURCE,
    EnvironmentCompatibilityDeclaration,
    EvidencePresenceDeclaration,
    OutcomePolicyDeclaration,
    ProfileConditionDeclaration,
    RequiredEvidenceBinding,
    ReviewPolicyDeclaration,
    SourceBoundaryAssignment,
)
from belgi.profile.reference_profile.identifiers.authority import AUTHORITATIVE
from belgi.profile.reference_profile.identifiers.boundary import INCLUDED
from belgi.profile.reference_profile.identifiers.conditions import (
    ANALYSIS_POLICY_SATISFIED,
    BUILD_POLICY_SATISFIED,
    COVERAGE_POLICY_SATISFIED,
    DEPENDENCY_POLICY_SATISFIED,
    TEST_POLICY_SATISFIED,
)

__all__ = [
    "reference_profile_evaluator_dependency_bindings",
    "reference_profile_evaluator_dependency_designators",
    "validate_reference_profile_evaluator_carrier",
    "validate_reference_profile_source_boundary_assignments",
]


_DEVELOPER_WORKSPACE_PROHIBITED_CONDITIONS = frozenset(
    {
        ANALYSIS_POLICY_SATISFIED,
        BUILD_POLICY_SATISFIED,
        COVERAGE_POLICY_SATISFIED,
        DEPENDENCY_POLICY_SATISFIED,
        TEST_POLICY_SATISFIED,
    }
)


def _carrier_designator_from_binding(
    *,
    binding: ExactEditionBinding,
) -> ImmutableDesignator:
    return binding.immutable_designator


def _designator_key(*, designator: object) -> tuple[str, str, str] | None:
    uri = getattr(designator, "uri", None)
    digest = getattr(designator, "digest", None)
    algorithm_id = getattr(digest, "algorithm_id", None)
    digest_value = getattr(digest, "digest_value", None)
    if not isinstance(uri, str):
        return None
    if not isinstance(algorithm_id, str):
        return None
    if not isinstance(digest_value, str):
        return None
    return (uri, algorithm_id, digest_value)


def _required_evidence_bindings(
    *,
    declaration: ProfileConditionDeclaration,
) -> tuple[RequiredEvidenceBinding, ...]:
    if isinstance(
        declaration,
        (
            EvidencePresenceDeclaration,
            OutcomePolicyDeclaration,
            ReviewPolicyDeclaration,
            EnvironmentCompatibilityDeclaration,
        ),
    ):
        return declaration.required_bindings
    return ()


def _uses_authoritative_ci_binding(
    *,
    declaration: ProfileConditionDeclaration,
) -> bool:
    return any(
        binding.minimum_authority == AUTHORITATIVE
        and CI_EXECUTION_SOURCE in binding.allowed_source_classes
        for binding in _required_evidence_bindings(declaration=declaration)
    )


def reference_profile_evaluator_dependency_bindings(
    *,
    condition_declarations: tuple[ProfileConditionDeclaration, ...],
) -> tuple[ExactEditionBinding, ...]:
    ordered: list[ExactEditionBinding] = []
    seen: set[ExactEditionBinding] = set()
    for declaration in condition_declarations:
        for dependency in declaration.replay_relevant_dependencies:
            if dependency in seen:
                continue
            seen.add(dependency)
            ordered.append(dependency)
    return tuple(ordered)


def reference_profile_evaluator_dependency_designators(
    *,
    condition_declarations: tuple[ProfileConditionDeclaration, ...],
) -> tuple[ImmutableDesignator, ...]:
    return tuple(
        _carrier_designator_from_binding(binding=binding)
        for binding in reference_profile_evaluator_dependency_bindings(
            condition_declarations=condition_declarations
        )
    )


def validate_reference_profile_source_boundary_assignments(
    *,
    source_boundary_assignments: tuple[SourceBoundaryAssignment, ...],
    condition_declarations: tuple[ProfileConditionDeclaration, ...],
) -> None:
    authoritative_workspace = any(
        assignment.source_class == DEVELOPER_WORKSPACE_SOURCE
        and assignment.boundary_participation == INCLUDED
        and assignment.authority_level == AUTHORITATIVE
        for assignment in source_boundary_assignments
    )
    if not authoritative_workspace:
        return
    prohibited = sorted(
        str(declaration.condition_id)
        for declaration in condition_declarations
        if declaration.condition_id in _DEVELOPER_WORKSPACE_PROHIBITED_CONDITIONS
    )
    if prohibited:
        raise ValueError(
            "developer-workspace evidence must not be authoritative for: "
            + ", ".join(prohibited)
        )


def validate_reference_profile_evaluator_carrier(
    *,
    evaluator_carrier: object,
    condition_declarations: tuple[ProfileConditionDeclaration, ...],
) -> None:
    exact_edition_designators = getattr(
        evaluator_carrier, "exact_edition_designators", ()
    )
    if not isinstance(exact_edition_designators, tuple):
        exact_edition_designators = tuple(exact_edition_designators)
    preserved_designators = frozenset(
        designator_key
        for designator in exact_edition_designators
        if (designator_key := _designator_key(designator=designator)) is not None
    )
    for declaration in condition_declarations:
        if not _uses_authoritative_ci_binding(declaration=declaration):
            continue
        if not declaration.replay_relevant_dependencies:
            raise ValueError(
                "authoritative ci-execution bindings require at least one replay-relevant "
                f"exact-edition dependency for {declaration.condition_id!s}."
            )
        for dependency in declaration.replay_relevant_dependencies:
            designator = _carrier_designator_from_binding(binding=dependency)
            designator_key = _designator_key(designator=designator)
            if designator_key not in preserved_designators:
                raise ValueError(
                    "evaluator carrier is missing exact-edition dependency "
                    f"{designator!s} required by {declaration.condition_id!s}."
                )
