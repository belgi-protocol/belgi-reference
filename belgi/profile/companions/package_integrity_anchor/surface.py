from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from belgi.profile.edition import Digest, ImmutableDesignator

from .constants import (
    ED25519_SIGNATURE_ALGORITHM_IDENTIFIER,
    PACKAGE_INTEGRITY_ALGORITHM_SOURCE_SHA256,
    PACKAGE_INTEGRITY_ALGORITHM_SOURCE_URI,
    PACKAGE_INTEGRITY_VERIFICATION_METHOD_IDENTIFIER,
    PREDECESSOR_PACKAGE_INTEGRITY_VERIFICATION_METHOD_IDENTIFIER,
    SHA256_DIGEST_ALGORITHM_IDENTIFIER,
)
from .exceptions import (
    DeprecatedPackageIntegrityMethodError,
    SignatureAlgorithmSourceMismatchError,
    UnsupportedPackageIntegritySurfaceError,
    VerificationMethodSourceMismatchError,
)
from .source_binding import (
    DesignatorSurface,
    ExactSourceBinding,
    exact_source_binding_from_designator,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class SupportedPackageIntegritySurface:
    verification_method_identifier: str
    digest_algorithm_identifier: str
    signature_algorithm_identifier: str
    verification_method_source: ExactSourceBinding
    digest_algorithm_source: ExactSourceBinding
    signature_algorithm_source: ExactSourceBinding


def _algorithm_source() -> ExactSourceBinding:
    source_path = (
        Path(__file__).resolve().parents[2]
        / "editions/spec-0.3"
        / f"sha256-{PACKAGE_INTEGRITY_ALGORITHM_SOURCE_SHA256}"
        / "BELGI-Companion-Package-Integrity-Anchor-Verification.md"
    )
    return exact_source_binding_from_designator(
        identifier=ED25519_SIGNATURE_ALGORITHM_IDENTIFIER,
        designator=ImmutableDesignator(
            uri=PACKAGE_INTEGRITY_ALGORITHM_SOURCE_URI,
            digest=Digest(
                algorithm_id="sha256",
                digest_value=PACKAGE_INTEGRITY_ALGORITHM_SOURCE_SHA256,
            ),
        ),
        source_bytes=source_path.read_bytes(),
    )


def supported_package_integrity_surface(
    *,
    companion_source_designator: DesignatorSurface,
    companion_source_bytes: bytes,
) -> SupportedPackageIntegritySurface:
    method_source = exact_source_binding_from_designator(
        identifier=PACKAGE_INTEGRITY_VERIFICATION_METHOD_IDENTIFIER,
        designator=companion_source_designator,
        source_bytes=companion_source_bytes,
    )
    algorithm_source = _algorithm_source()
    return SupportedPackageIntegritySurface(
        verification_method_identifier=(
            PACKAGE_INTEGRITY_VERIFICATION_METHOD_IDENTIFIER
        ),
        digest_algorithm_identifier=SHA256_DIGEST_ALGORITHM_IDENTIFIER,
        signature_algorithm_identifier=ED25519_SIGNATURE_ALGORITHM_IDENTIFIER,
        verification_method_source=method_source,
        digest_algorithm_source=algorithm_source,
        signature_algorithm_source=algorithm_source,
    )


def select_package_integrity_surface(
    *,
    requested_verification_method: str,
    requested_verification_method_source_uri: str,
    requested_signature_algorithm: str,
    requested_signature_algorithm_source_uri: str,
    supported_surface: SupportedPackageIntegritySurface,
) -> SupportedPackageIntegritySurface:
    if (
        requested_verification_method
        == PREDECESSOR_PACKAGE_INTEGRITY_VERIFICATION_METHOD_IDENTIFIER
    ):
        raise DeprecatedPackageIntegrityMethodError(
            "The predecessor package-integrity method is prohibited for new use."
        )
    if (
        requested_verification_method
        != supported_surface.verification_method_identifier
        or requested_signature_algorithm
        != supported_surface.signature_algorithm_identifier
    ):
        raise UnsupportedPackageIntegritySurfaceError(
            "The requested package-integrity method and algorithm pair is unsupported."
        )
    if (
        requested_verification_method_source_uri
        != supported_surface.verification_method_source.uri
    ):
        raise VerificationMethodSourceMismatchError(
            "The verification-method identifier is paired with another source."
        )
    if (
        requested_signature_algorithm_source_uri
        != supported_surface.signature_algorithm_source.uri
    ):
        raise SignatureAlgorithmSourceMismatchError(
            "The signature-algorithm identifier is paired with another source."
        )
    return supported_surface


__all__ = [
    "SupportedPackageIntegritySurface",
    "select_package_integrity_surface",
    "supported_package_integrity_surface",
]
