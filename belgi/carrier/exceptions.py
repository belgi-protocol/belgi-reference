"""Carrier-layer exception hierarchy."""

from __future__ import annotations

__all__ = [
    "CanonicalReferenceError",
    "CarrierError",
    "ClaimRecordError",
    "ClosureError",
    "DependencyDeclarationError",
    "DuplicateCanonicalReferenceError",
    "DuplicateMemberNameError",
    "EvaluatorCarrierError",
    "EvidenceCarrierError",
    "IntegrityError",
    "InvalidContentLocatorError",
    "InvalidDeclarationParameterError",
    "InvalidDigestError",
    "InvalidInventoryEntryError",
    "InvalidMemberDraftError",
    "InvalidMemberNameError",
    "InvalidProjectionSpecError",
    "InvalidRepresentationBindingError",
    "JudgedCarrierError",
    "MemberError",
    "OpenReplayPackageError",
    "PackageAssemblyError",
    "PackageIntegrityAnchorError",
    "PackageIntegrityManifestError",
    "ProjectionError",
    "ReferencedSourceError",
    "RootDesignationError",
    "UnsupportedCanonicalizationError",
    "UnsupportedIntegrityAlgorithmError",
]


class CarrierError(Exception):
    """Base exception for the BELGI carrier layer."""


class MemberError(CarrierError):
    """Base exception for member and inventory failures."""


class InvalidMemberNameError(MemberError):
    """Raised when a member name is blank or otherwise unusable."""


class DuplicateMemberNameError(MemberError):
    """Raised when package-local member names are not unique."""


class InvalidContentLocatorError(MemberError):
    """Raised when a content locator is internally inconsistent."""


class InvalidDeclarationParameterError(MemberError):
    """Raised when a declaration parameter is malformed."""


class InvalidRepresentationBindingError(MemberError):
    """Raised when a representation binding is malformed."""


class InvalidDigestError(MemberError):
    """Raised when a digest is malformed."""


class InvalidMemberDraftError(MemberError):
    """Raised when a member draft cannot represent a valid preserved member."""


class InvalidInventoryEntryError(MemberError):
    """Raised when a member inventory entry violates Part 2 invariants."""


class ProjectionError(CarrierError):
    """Base exception for replay-relevant projection failures."""


class InvalidProjectionSpecError(ProjectionError):
    """Raised when a projection specification is internally inconsistent."""


class IntegrityError(CarrierError):
    """Base exception for integrity-binding failures."""


class UnsupportedCanonicalizationError(IntegrityError):
    """Raised when a requested canonicalization method is not supported."""


class UnsupportedIntegrityAlgorithmError(IntegrityError):
    """Raised when an unsupported integrity algorithm designator is requested."""


class CanonicalReferenceError(CarrierError):
    """Base exception for canonical-reference assignment failures."""


class DuplicateCanonicalReferenceError(CanonicalReferenceError):
    """Raised when canonical-reference assignment would collide."""


class JudgedCarrierError(CarrierError):
    """Raised when a judged-object carrier is malformed."""


class EvidenceCarrierError(CarrierError):
    """Raised when an evidence-state carrier is malformed."""


class EvaluatorCarrierError(CarrierError):
    """Raised when an evaluator carrier is malformed."""


class ClaimRecordError(CarrierError):
    """Base exception for claim-record failures."""


class RootDesignationError(ClaimRecordError):
    """Raised when required root designators are missing or inconsistent."""


class DependencyDeclarationError(ClaimRecordError):
    """Raised when dependency declarations are inconsistent with the inventory."""


class ReferencedSourceError(ClaimRecordError):
    """Raised when referenced-source bindings are malformed or incomplete."""


class PackageIntegrityManifestError(CarrierError):
    """Raised when a package-integrity manifest is malformed or inconsistent."""


class PackageIntegrityAnchorError(CarrierError):
    """Raised when a package-integrity anchor is malformed or inconsistent."""


class ClosureError(CarrierError):
    """Base exception for package-closure failures."""


class OpenReplayPackageError(ClosureError):
    """Raised when a replay package is not closed under replay-relevant dependencies."""


class PackageAssemblyError(CarrierError):
    """Raised when replay-package assembly cannot produce a valid closure unit."""
