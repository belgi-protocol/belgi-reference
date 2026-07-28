from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol

from belgi.substrate.base64 import decode_canonical_base64
from belgi.substrate.crypto import (
    parse_ed25519_public_key_hex,
    verify_ed25519_signature,
)
from belgi.substrate.exceptions import (
    Base64EncodingError,
    CryptoDependencyError,
    Ed25519KeyError,
    Ed25519SignatureError,
    HexEncodingError,
)
from belgi.substrate.hash import sha256_bytes
from belgi.substrate.hex import decode_lowercase_hex

from .constants import DESIGNATOR_DIGEST_ALGORITHM_TOKEN
from .exceptions import (
    SignatureAlgorithmSourceMismatchError,
    UnsupportedPackageIntegritySurfaceError,
    VerificationMethodSourceMismatchError,
)
from .source_binding import DesignatorSurface
from .surface import (
    SupportedPackageIntegritySurface,
    select_package_integrity_surface,
)

PackageIntegrityVerificationCode = Literal[
    "accepted",
    "method-or-algorithm-unsupported",
    "method-source-mismatch",
    "algorithm-source-mismatch",
    "key-designator-malformed",
    "key-binding-mismatch",
    "key-malformed",
    "signature-malformed",
    "signature-invalid",
    "crypto-unavailable",
]


class _PackageIntegrityAnchorSurface(Protocol):
    @property
    def verification_method_identifier(self) -> str: ...

    @property
    def verification_method_designator(self) -> DesignatorSurface: ...

    @property
    def signature_algorithm_identifier(self) -> str: ...

    @property
    def signature_algorithm_designator(self) -> DesignatorSurface: ...

    @property
    def verification_key_designator(self) -> DesignatorSurface: ...

    @property
    def verification_key_text(self) -> str: ...

    @property
    def signature_base64(self) -> str: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class PackageIntegrityVerificationOutcome:
    accepted: bool
    code: PackageIntegrityVerificationCode
    detail: str

    def __post_init__(self) -> None:
        if self.accepted != (self.code == "accepted"):
            raise ValueError("Only the accepted outcome may use the accepted code.")


def _rejected(
    code: PackageIntegrityVerificationCode,
    detail: str,
) -> PackageIntegrityVerificationOutcome:
    return PackageIntegrityVerificationOutcome(
        accepted=False,
        code=code,
        detail=detail,
    )


def verify_package_integrity_anchor_manifest(
    *,
    anchor: _PackageIntegrityAnchorSurface,
    manifest_bytes: bytes,
    supported_surface: SupportedPackageIntegritySurface,
) -> PackageIntegrityVerificationOutcome:
    """Verify exact manifest octets under one independently supplied surface."""

    selection = select_package_integrity_anchor_surface(
        anchor=anchor,
        supported_surface=supported_surface,
    )
    if not selection.accepted:
        return selection

    key_digest = anchor.verification_key_designator.digest
    if key_digest.algorithm_id != DESIGNATOR_DIGEST_ALGORITHM_TOKEN:
        return _rejected(
            "key-designator-malformed",
            "Verification-key designator must use the exact sha256 token.",
        )
    try:
        decode_lowercase_hex(text=key_digest.digest_value, exact_octets=32)
    except HexEncodingError as exc:
        return _rejected("key-designator-malformed", str(exc))
    key_text_bytes = anchor.verification_key_text.encode("utf-8")
    if sha256_bytes(key_text_bytes) != key_digest.digest_value:
        return _rejected(
            "key-binding-mismatch",
            "Verification-key designator does not bind the exact key text.",
        )
    try:
        public_key = parse_ed25519_public_key_hex(anchor.verification_key_text)
    except Ed25519KeyError as exc:
        return _rejected("key-malformed", str(exc))
    try:
        signature = decode_canonical_base64(
            text=anchor.signature_base64,
            exact_octets=64,
        )
    except Base64EncodingError as exc:
        return _rejected("signature-malformed", str(exc))
    try:
        verify_ed25519_signature(
            public_key,
            signature,
            manifest_bytes,
            context="package-integrity anchor manifest",
        )
    except Ed25519SignatureError as exc:
        return _rejected("signature-invalid", str(exc))
    except CryptoDependencyError as exc:
        return _rejected("crypto-unavailable", str(exc))
    return PackageIntegrityVerificationOutcome(
        accepted=True,
        code="accepted",
        detail="Pure Ed25519 signature verified over the exact manifest octets.",
    )


def select_package_integrity_anchor_surface(
    *,
    anchor: _PackageIntegrityAnchorSurface,
    supported_surface: SupportedPackageIntegritySurface,
) -> PackageIntegrityVerificationOutcome:
    """Select the exact method, algorithm, and defining sources without crypto."""

    try:
        selected = select_package_integrity_surface(
            requested_verification_method=anchor.verification_method_identifier,
            requested_verification_method_source_uri=(
                anchor.verification_method_designator.uri
            ),
            requested_signature_algorithm=anchor.signature_algorithm_identifier,
            requested_signature_algorithm_source_uri=(
                anchor.signature_algorithm_designator.uri
            ),
            supported_surface=supported_surface,
        )
    except VerificationMethodSourceMismatchError as exc:
        return _rejected("method-source-mismatch", str(exc))
    except SignatureAlgorithmSourceMismatchError as exc:
        return _rejected("algorithm-source-mismatch", str(exc))
    except UnsupportedPackageIntegritySurfaceError as exc:
        return _rejected("method-or-algorithm-unsupported", str(exc))
    if not selected.verification_method_source.matches(
        designator=anchor.verification_method_designator
    ):
        return _rejected(
            "method-source-mismatch",
            "Verification-method designator does not match the supported exact source.",
        )
    if not selected.signature_algorithm_source.matches(
        designator=anchor.signature_algorithm_designator
    ):
        return _rejected(
            "algorithm-source-mismatch",
            "Signature-algorithm designator does not match the supported exact source.",
        )
    return PackageIntegrityVerificationOutcome(
        accepted=True,
        code="accepted",
        detail="Exact package-integrity method and source surface selected.",
    )


__all__ = [
    "PackageIntegrityVerificationCode",
    "PackageIntegrityVerificationOutcome",
    "select_package_integrity_anchor_surface",
    "verify_package_integrity_anchor_manifest",
]
