from __future__ import annotations

from belgi.profile.edition import (
    ImmutableDesignator,
    VersionDesignator,
    external_edition_binding,
)
from belgi.profile.extension_points import (
    REPRESENTATION_SPECIFIC_SCHEMAS_AND_SERIALIZATION_BINDINGS,
)
from belgi.profile.governance import (
    CompanionSpecification,
    DeclarationSurface,
    DependencyReference,
    validate_companion_specification,
)

from .edition import (
    COMPANION_CONFORMANCE_REQUIREMENTS,
    build_package_integrity_anchor_companion_edition,
)

__all__ = [
    "SIGNATURE_VERIFICATION_METHOD_SURFACE_ID",
    "build_package_integrity_anchor_companion_specification",
]


SIGNATURE_VERIFICATION_METHOD_SURFACE_ID = (
    "package-integrity-anchor.signature-verification-method"
)


def build_package_integrity_anchor_companion_specification(
    *,
    companion_immutable_designator: ImmutableDesignator,
    belgi_part_2_designator: ImmutableDesignator,
    belgi_part_3_designator: ImmutableDesignator,
    exact_dependencies: tuple[DependencyReference, ...] = (),
) -> CompanionSpecification:
    specification = CompanionSpecification(
        edition=build_package_integrity_anchor_companion_edition(
            immutable_designator=companion_immutable_designator,
        ),
        served_extension_points=(
            REPRESENTATION_SPECIFIC_SCHEMAS_AND_SERIALIZATION_BINDINGS,
        ),
        declarations=(
            DeclarationSurface(
                identifier=SIGNATURE_VERIFICATION_METHOD_SURFACE_ID,
                extension_point=REPRESENTATION_SPECIFIC_SCHEMAS_AND_SERIALIZATION_BINDINGS,
                mandatory=True,
            ),
        ),
        conformance_requirements=COMPANION_CONFORMANCE_REQUIREMENTS,
        exact_dependencies=(
            DependencyReference(
                binding=external_edition_binding(
                    identifier="https://belgi.dev/ids/specification/part-2",
                    version=VersionDesignator("0.5"),
                    immutable_designator=belgi_part_2_designator,
                ),
                replay_relevant=True,
                clause_locator="Package-integrity manifest and anchor model",
            ),
            DependencyReference(
                binding=external_edition_binding(
                    identifier="https://belgi.dev/ids/specification/part-3",
                    version=VersionDesignator("0.5"),
                    immutable_designator=belgi_part_3_designator,
                ),
                replay_relevant=True,
                clause_locator="Companion governance",
            ),
            *exact_dependencies,
        ),
        prohibited_redefinitions=frozenset(),
    )
    validate_companion_specification(specification=specification)
    return specification
