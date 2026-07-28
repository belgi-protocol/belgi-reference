from __future__ import annotations

from pathlib import Path

from belgi.profile.companions.package_integrity_anchor.surface import (
    SupportedPackageIntegritySurface,
    supported_package_integrity_surface,
)
from belgi.profile.edition import Digest, ImmutableDesignator

_CORPUS_METHOD_SOURCE_SHA256 = (
    "490fab5cb1f83dd6ae849b44a2805703e9b5f334ca6dc4dd855b706cd069583f"
)
_CORPUS_METHOD_SOURCE_URI = (
    "https://belgi.dev/specs/spec-0.4/"
    f"sha256-{_CORPUS_METHOD_SOURCE_SHA256}/"
    "BELGI-Companion-Package-Integrity-Anchor-Verification.md"
)


def built_in_package_integrity_crypto_surface() -> SupportedPackageIntegritySurface:
    source_path = (
        Path(__file__).resolve().parents[3]
        / "editions/spec-0.4"
        / f"sha256-{_CORPUS_METHOD_SOURCE_SHA256}"
        / "BELGI-Companion-Package-Integrity-Anchor-Verification.md"
    )
    return supported_package_integrity_surface(
        companion_source_designator=ImmutableDesignator(
            uri=_CORPUS_METHOD_SOURCE_URI,
            digest=Digest(
                algorithm_id="sha256",
                digest_value=_CORPUS_METHOD_SOURCE_SHA256,
            ),
        ),
        companion_source_bytes=source_path.read_bytes(),
    )


__all__ = ["built_in_package_integrity_crypto_surface"]
