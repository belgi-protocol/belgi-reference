from __future__ import annotations

from belgi.profile.edition import (
    ExactEditionBinding,
    ImmutableDesignator,
    VersionDesignator,
    external_edition_binding,
)
from belgi.profile.extension_points import (
    ENVIRONMENT_ENVELOPE_VOCABULARY,
    TRUST_BOUNDARY_VOCABULARY,
)
from belgi.profile.governance import (
    CompanionSpecification,
    DeclarationSurface,
    DependencyReference,
    validate_companion_specification,
)

from .edition import (
    COMPANION_CONFORMANCE_REQUIREMENTS,
    build_ci_trust_companion_edition,
)

__all__ = ["build_ci_trust_companion_specification"]


def build_ci_trust_companion_specification(
    *,
    companion_immutable_designator: ImmutableDesignator,
    belgi_part_3_designator: ImmutableDesignator,
    profile_dependency_binding: ExactEditionBinding,
    exact_dependencies: tuple[DependencyReference, ...] = (),
) -> CompanionSpecification:
    specification = CompanionSpecification(
        edition=build_ci_trust_companion_edition(
            immutable_designator=companion_immutable_designator,
        ),
        served_extension_points=(
            TRUST_BOUNDARY_VOCABULARY,
            ENVIRONMENT_ENVELOPE_VOCABULARY,
        ),
        declarations=(
            DeclarationSurface(
                identifier="ci-trust.source-material-role-vocabulary",
                extension_point=TRUST_BOUNDARY_VOCABULARY,
                mandatory=True,
            ),
            DeclarationSurface(
                identifier="ci-trust.environment-vocabulary",
                extension_point=ENVIRONMENT_ENVELOPE_VOCABULARY,
                mandatory=True,
            ),
            DeclarationSurface(
                identifier="ci-trust.default-declarations",
                extension_point=TRUST_BOUNDARY_VOCABULARY,
                mandatory=False,
            ),
        ),
        conformance_requirements=COMPANION_CONFORMANCE_REQUIREMENTS,
        exact_dependencies=(
            DependencyReference(
                binding=external_edition_binding(
                    identifier="https://belgi.dev/ids/specification/part-3",
                    version=VersionDesignator("0.5"),
                    immutable_designator=belgi_part_3_designator,
                ),
                replay_relevant=True,
                clause_locator="Companion governance",
            ),
            DependencyReference(
                binding=profile_dependency_binding,
                replay_relevant=True,
                clause_locator="Generic profile trust-boundary refinement",
            ),
            *exact_dependencies,
        ),
        prohibited_redefinitions=frozenset(),
    )
    validate_companion_specification(specification=specification)
    return specification
