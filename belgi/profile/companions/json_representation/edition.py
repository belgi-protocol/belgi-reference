from __future__ import annotations

from belgi.profile.edition import (
    CompanionIdentifier,
    ExactEdition,
    ImmutableDesignator,
    PublisherIdentifier,
    VersionDesignator,
    companion_edition,
)

__all__ = [
    "COMPANION_IDENTIFIER",
    "COMPANION_SCOPE",
    "COMPANION_TITLE",
    "COMPANION_VERSION",
    "build_json_representation_companion_edition",
]


COMPANION_IDENTIFIER = CompanionIdentifier(
    "https://belgi.dev/ids/companion/json-representation"
)
COMPANION_VERSION = VersionDesignator("0.5")
COMPANION_TITLE = "BELGI Companion JSON Representation"
COMPANION_SCOPE = (
    "Representation rules and physical replay-package projection procedures."
)
_BELGI_PUBLISHER = PublisherIdentifier("belgi")


def build_json_representation_companion_edition(
    *,
    immutable_designator: ImmutableDesignator,
    owning_publisher: PublisherIdentifier = _BELGI_PUBLISHER,
) -> ExactEdition:
    return companion_edition(
        identifier=COMPANION_IDENTIFIER,
        version=COMPANION_VERSION,
        immutable_designator=immutable_designator,
        title=COMPANION_TITLE,
        scope=COMPANION_SCOPE,
        owning_publisher=owning_publisher,
    )
