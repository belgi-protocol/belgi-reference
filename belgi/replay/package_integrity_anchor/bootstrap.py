from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier import ImmutableDesignator, PackageIntegrityAnchor
from belgi.profile.companions.package_integrity_anchor.constants import (
    SHA256_DIGEST_ALGORITHM_IDENTIFIER,
)
from belgi.profile.companions.package_integrity_anchor.edition import (
    COMPANION_IDENTIFIER,
    COMPANION_VERSION,
    build_package_integrity_anchor_companion_binding,
    require_package_integrity_anchor_companion,
)
from belgi.profile.companions.package_integrity_anchor.surface import (
    SupportedPackageIntegritySurface,
    supported_package_integrity_surface,
)
from belgi.profile.companions.package_integrity_anchor.verification import (
    PackageIntegrityVerificationOutcome,
    select_package_integrity_anchor_surface,
    verify_package_integrity_anchor_manifest,
)
from belgi.profile.edition import ExactEditionBinding
from belgi.profile.edition_catalog import exact_edition_documents
from belgi.profile.source_material import built_in_exact_edition_source
from belgi.replay.context import PackageIntegrityAnchorVerifier


@dataclass(frozen=True, slots=True, kw_only=True)
class _ExactPackageIntegrityAnchorVerifier:
    supported_surface: SupportedPackageIntegritySurface

    def __call__(
        self,
        *,
        anchor: PackageIntegrityAnchor,
        manifest_bytes: bytes,
    ) -> PackageIntegrityVerificationOutcome:
        return verify_package_integrity_anchor_manifest(
            anchor=anchor,
            manifest_bytes=manifest_bytes,
            supported_surface=self.supported_surface,
        )

    def select(
        self,
        *,
        anchor: PackageIntegrityAnchor,
    ) -> PackageIntegrityVerificationOutcome:
        return select_package_integrity_anchor_surface(
            anchor=anchor,
            supported_surface=self.supported_surface,
        )

    def supports_digest_algorithm_identifier(self, *, identifier: str) -> bool:
        return identifier == self.supported_surface.digest_algorithm_identifier

    def supports_digest_algorithm_designator(
        self,
        *,
        designator: ImmutableDesignator,
    ) -> bool:
        return (
            self.supported_surface.digest_algorithm_identifier
            == SHA256_DIGEST_ALGORITHM_IDENTIFIER
            and self.supported_surface.digest_algorithm_source.matches(
                designator=designator
            )
        )


def package_integrity_anchor_verifier_for_source(
    *,
    companion_binding: ExactEditionBinding,
    companion_source_bytes: bytes,
) -> PackageIntegrityAnchorVerifier:
    """Bind replay capability to one caller-supplied exact companion source."""

    selected_binding = require_package_integrity_anchor_companion(
        selected_companions=(companion_binding,)
    )
    return _ExactPackageIntegrityAnchorVerifier(
        supported_surface=supported_package_integrity_surface(
            companion_source_designator=selected_binding.immutable_designator,
            companion_source_bytes=companion_source_bytes,
        )
    )


def installed_package_integrity_anchor_verifier() -> PackageIntegrityAnchorVerifier:
    """Bind replay to independently installed exact-edition source bytes."""

    matches = tuple(
        document
        for document in exact_edition_documents()
        if document.family_identifier == str(COMPANION_IDENTIFIER)
        and document.version_designator == str(COMPANION_VERSION)
        and document.kind == "companion"
    )
    if len(matches) != 1:
        raise ValueError(
            "installed exact-edition catalog must contain exactly one supported "
            "package-integrity-anchor companion."
        )
    companion_binding = build_package_integrity_anchor_companion_binding(
        immutable_designator=matches[0].immutable_designator
    )
    companion_source = built_in_exact_edition_source(binding=companion_binding)
    return package_integrity_anchor_verifier_for_source(
        companion_binding=companion_binding,
        companion_source_bytes=companion_source.preserved_bytes,
    )


__all__ = [
    "installed_package_integrity_anchor_verifier",
    "package_integrity_anchor_verifier_for_source",
]
