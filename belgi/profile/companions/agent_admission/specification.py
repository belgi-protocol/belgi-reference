from __future__ import annotations

from belgi.profile.edition import (
    ExactEditionBinding,
    ImmutableDesignator,
    VersionDesignator,
    external_edition_binding,
)
from belgi.profile.extension_points import (
    CONDITION_VOCABULARY,
    ENVIRONMENT_ENVELOPE_VOCABULARY,
    EVALUATOR_DECLARATION_PARAMETER_VOCABULARY,
    EVIDENCE_VOCABULARY_AND_EVIDENCE_KINDS,
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
    build_agent_admission_companion_edition,
)

__all__ = ["build_agent_admission_companion_specification"]


def build_agent_admission_companion_specification(
    *,
    companion_immutable_designator: ImmutableDesignator,
    belgi_part_3_designator: ImmutableDesignator,
    profile_dependency_binding: ExactEditionBinding,
    exact_dependencies: tuple[DependencyReference, ...] = (),
) -> CompanionSpecification:
    specification = CompanionSpecification(
        edition=build_agent_admission_companion_edition(
            immutable_designator=companion_immutable_designator,
        ),
        served_extension_points=(
            EVIDENCE_VOCABULARY_AND_EVIDENCE_KINDS,
            CONDITION_VOCABULARY,
            TRUST_BOUNDARY_VOCABULARY,
            ENVIRONMENT_ENVELOPE_VOCABULARY,
            EVALUATOR_DECLARATION_PARAMETER_VOCABULARY,
        ),
        declarations=(
            DeclarationSurface(
                identifier="agent-admission.condition-vocabulary",
                extension_point=CONDITION_VOCABULARY,
                mandatory=True,
            ),
            DeclarationSurface(
                identifier="agent-admission.evidence-vocabulary",
                extension_point=EVIDENCE_VOCABULARY_AND_EVIDENCE_KINDS,
                mandatory=True,
            ),
            DeclarationSurface(
                identifier="agent-admission.trust-boundary-vocabulary",
                extension_point=TRUST_BOUNDARY_VOCABULARY,
                mandatory=True,
            ),
            DeclarationSurface(
                identifier="agent-admission.environment-vocabulary",
                extension_point=ENVIRONMENT_ENVELOPE_VOCABULARY,
                mandatory=True,
            ),
            DeclarationSurface(
                identifier="agent-admission.parameter-vocabulary",
                extension_point=EVALUATOR_DECLARATION_PARAMETER_VOCABULARY,
                mandatory=True,
            ),
            DeclarationSurface(
                identifier="agent-admission.default-declarations",
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
                clause_locator="Generic profile semantic reuse",
            ),
            *exact_dependencies,
        ),
        prohibited_redefinitions=frozenset(),
    )
    validate_companion_specification(specification=specification)
    return specification
