from __future__ import annotations

from belgi.profile.edition import (
    CompanionIdentifier,
    ExactEdition,
    ImmutableDesignator,
    PublisherIdentifier,
    VersionDesignator,
    companion_edition,
)
from belgi.profile.governance import ConformanceRequirementId

__all__ = [
    "COMPANION_CONFORMANCE_REQUIREMENTS",
    "COMPANION_IDENTIFIER",
    "COMPANION_SCOPE",
    "COMPANION_TITLE",
    "COMPANION_VERSION",
    "build_python_companion_edition",
]


COMPANION_IDENTIFIER = CompanionIdentifier(
    "https://belgi.dev/ids/companion/python-condition-vocabulary"
)
COMPANION_VERSION = VersionDesignator("0.5")
COMPANION_TITLE = "BELGI Companion Python Condition Vocabulary"
COMPANION_SCOPE = (
    "Python-specific condition, evidence-kind, parameter, and semantics vocabulary."
)
COMPANION_CONFORMANCE_REQUIREMENTS = (
    ConformanceRequirementId("belgi.python-companion.conformance.specification"),
)
_BELGI_PUBLISHER = PublisherIdentifier("belgi")


def build_python_companion_edition(
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
