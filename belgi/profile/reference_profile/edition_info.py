from __future__ import annotations

from belgi.profile.edition import (
    ExactEdition,
    ExactEditionBinding,
    ImmutableDesignator,
    PublisherIdentifier,
    VersionDesignator,
    external_edition_binding,
    profile_edition,
    profile_edition_binding,
)

from .identifiers.profile import PROFILE_IDENTIFIER

__all__ = [
    "PROFILE_SCOPE",
    "PROFILE_TITLE",
    "PROFILE_VERSION",
    "build_reference_profile_belgi_dependencies",
    "build_reference_profile_binding",
    "build_reference_profile_edition",
]


PROFILE_VERSION = VersionDesignator("0.5")
PROFILE_TITLE = "BELGI Software Change Admission Profile"
PROFILE_SCOPE = "Generic BELGI profile for repository-based software change admission."
_BELGI_PUBLISHER = PublisherIdentifier("belgi")


def build_reference_profile_binding(
    *,
    immutable_designator: ImmutableDesignator,
) -> ExactEditionBinding:
    return profile_edition_binding(
        identifier=PROFILE_IDENTIFIER,
        version=PROFILE_VERSION,
        immutable_designator=immutable_designator,
    )


def build_reference_profile_edition(
    *,
    immutable_designator: ImmutableDesignator,
    owning_publisher: PublisherIdentifier = _BELGI_PUBLISHER,
) -> ExactEdition:
    return profile_edition(
        identifier=PROFILE_IDENTIFIER,
        version=PROFILE_VERSION,
        immutable_designator=immutable_designator,
        title=PROFILE_TITLE,
        scope=PROFILE_SCOPE,
        owning_publisher=owning_publisher,
    )


def build_reference_profile_belgi_dependencies(
    *,
    belgi_part_1_designator: ImmutableDesignator,
    belgi_part_2_designator: ImmutableDesignator,
    belgi_part_3_designator: ImmutableDesignator,
) -> tuple[ExactEditionBinding, ...]:
    return (
        external_edition_binding(
            identifier="https://belgi.dev/ids/specification/part-1",
            version=VersionDesignator("0.5"),
            immutable_designator=belgi_part_1_designator,
        ),
        external_edition_binding(
            identifier="https://belgi.dev/ids/specification/part-2",
            version=VersionDesignator("0.5"),
            immutable_designator=belgi_part_2_designator,
        ),
        external_edition_binding(
            identifier="https://belgi.dev/ids/specification/part-3",
            version=VersionDesignator("0.5"),
            immutable_designator=belgi_part_3_designator,
        ),
    )
