from __future__ import annotations

from belgi.profile.edition import (
    CompanionIdentifier,
    EditionKind,
    ExactEdition,
    ExactEditionBinding,
    ImmutableDesignator,
    PublisherIdentifier,
    VersionDesignator,
    companion_edition,
    companion_edition_binding,
)
from belgi.profile.governance import ConformanceRequirementId

__all__ = [
    "COMPANION_IDENTIFIER",
    "COMPANION_SCOPE",
    "COMPANION_TITLE",
    "COMPANION_VERSION",
    "build_package_integrity_anchor_companion_binding",
    "build_package_integrity_anchor_companion_edition",
    "is_package_integrity_anchor_companion_binding",
    "require_package_integrity_anchor_companion",
]


COMPANION_IDENTIFIER = CompanionIdentifier(
    "https://belgi.dev/ids/companion/package-integrity-anchor-verification"
)
COMPANION_VERSION = VersionDesignator("0.5")
COMPANION_TITLE = "BELGI Companion Package Integrity Anchor Verification"
COMPANION_SCOPE = (
    "Representation-specific verification surface for the package-integrity "
    "manifest and package-integrity anchor."
)
COMPANION_CONFORMANCE_REQUIREMENTS = (
    ConformanceRequirementId(
        "belgi.package-integrity-anchor-companion.conformance.specification"
    ),
)
BELGI_PUBLISHER = PublisherIdentifier("belgi")


def build_package_integrity_anchor_companion_edition(
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


def build_package_integrity_anchor_companion_binding(
    *,
    immutable_designator: ImmutableDesignator,
) -> ExactEditionBinding:
    return companion_edition_binding(
        identifier=COMPANION_IDENTIFIER,
        version=COMPANION_VERSION,
        immutable_designator=immutable_designator,
    )


def is_package_integrity_anchor_companion_binding(
    *,
    binding: ExactEditionBinding,
) -> bool:
    return (
        binding.kind is EditionKind.COMPANION
        and str(binding.family_identifier) == str(COMPANION_IDENTIFIER)
        and str(binding.version_designator) == str(COMPANION_VERSION)
    )


def require_package_integrity_anchor_companion(
    *,
    selected_companions: tuple[ExactEditionBinding, ...],
) -> ExactEditionBinding:
    for binding in selected_companions:
        if is_package_integrity_anchor_companion_binding(binding=binding):
            return binding
    raise ValueError(
        "selected_companions must include the package-integrity-anchor verification companion exact edition."
    )
