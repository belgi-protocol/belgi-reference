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
    "BELGI_PUBLISHER",
    "COMPANION_CONFORMANCE_REQUIREMENTS",
    "COMPANION_IDENTIFIER",
    "COMPANION_SCOPE",
    "COMPANION_TITLE",
    "COMPANION_VERSION",
    "build_agent_admission_companion_edition",
]


COMPANION_IDENTIFIER = CompanionIdentifier(
    "https://belgi.dev/ids/companion/agent-admission"
)
COMPANION_VERSION = VersionDesignator("0.5")
COMPANION_TITLE = "BELGI Companion Agent Admission"
COMPANION_SCOPE = (
    "Agent-admission vocabulary and deterministic semantics over preserved "
    "agent-decision evidence. This companion does not replay live agent "
    "execution."
)
COMPANION_CONFORMANCE_REQUIREMENTS = (
    ConformanceRequirementId(
        "belgi.agent-admission-companion.conformance.specification"
    ),
)
BELGI_PUBLISHER = PublisherIdentifier("belgi")


def build_agent_admission_companion_edition(
    *,
    immutable_designator: ImmutableDesignator,
    owning_publisher: PublisherIdentifier = BELGI_PUBLISHER,
) -> ExactEdition:
    return companion_edition(
        identifier=COMPANION_IDENTIFIER,
        version=COMPANION_VERSION,
        immutable_designator=immutable_designator,
        title=COMPANION_TITLE,
        scope=COMPANION_SCOPE,
        owning_publisher=owning_publisher,
    )
