"""Package-integrity companion exceptions."""

from __future__ import annotations


class PackageIntegrityCompanionError(ValueError):
    """Base failure for the exact package-integrity companion surface."""


class ExactSourceBindingError(PackageIntegrityCompanionError):
    """Raised when a defining-source binding is not exact."""


class SourceIdentifierMismatchError(ExactSourceBindingError):
    """Raised when an identifier is paired with another identified source."""


class SourceDigestTextError(ExactSourceBindingError):
    """Raised when a defining-source digest is malformed or unsupported."""


class SourceDigestMismatchError(ExactSourceBindingError):
    """Raised when a defining-source digest does not bind the supplied bytes."""


class UnsupportedPackageIntegritySurfaceError(PackageIntegrityCompanionError):
    """Raised when exact method selection is unsupported."""


class DeprecatedPackageIntegrityMethodError(UnsupportedPackageIntegritySurfaceError):
    """Raised when the predecessor method is selected for new use."""


class VerificationMethodSourceMismatchError(UnsupportedPackageIntegritySurfaceError):
    """Raised when a method identifier is paired with another source."""


class SignatureAlgorithmSourceMismatchError(UnsupportedPackageIntegritySurfaceError):
    """Raised when an algorithm identifier is paired with another source."""


__all__ = [
    "DeprecatedPackageIntegrityMethodError",
    "ExactSourceBindingError",
    "PackageIntegrityCompanionError",
    "SignatureAlgorithmSourceMismatchError",
    "SourceDigestMismatchError",
    "SourceDigestTextError",
    "SourceIdentifierMismatchError",
    "UnsupportedPackageIntegritySurfaceError",
    "VerificationMethodSourceMismatchError",
]
