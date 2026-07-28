"""Carrier representation of one package-integrity anchor."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlparse

from belgi.carrier.exceptions import PackageIntegrityAnchorError
from belgi.carrier.inventory import (
    ImmutableDesignator,
    JsonCompatible,
    MemberName,
    PackageIdentifier,
    carrier_schema_designator,
    require_package_identifier,
)
from belgi.carrier.json_representation import (
    CarrierSchemaGraph,
    TrustedJSONRole,
    validate_carrier_json,
    validate_json_representation,
)
from belgi.carrier.parse_support import (
    parse_immutable_designator_object,
    require_allowed_keys,
    require_non_empty_text,
)
from belgi.substrate.base64 import decode_canonical_base64
from belgi.substrate.exceptions import Base64EncodingError, HexEncodingError
from belgi.substrate.hex import decode_lowercase_hex

from .binding import canonical_json_document_bytes

__all__ = [
    "PACKAGE_INTEGRITY_ANCHOR_KIND",
    "PACKAGE_INTEGRITY_ANCHOR_MEDIA_TYPE",
    "PACKAGE_INTEGRITY_ANCHOR_SCHEMA_DESIGNATOR",
    "PackageIntegrityAnchor",
    "parse_package_integrity_anchor_bootstrap_bytes",
    "parse_package_integrity_anchor_bytes",
]


PACKAGE_INTEGRITY_ANCHOR_KIND = "package-integrity-anchor"
PACKAGE_INTEGRITY_ANCHOR_MEDIA_TYPE = (
    "application/vnd.belgi.package-integrity-anchor+json"
)
PACKAGE_INTEGRITY_ANCHOR_SCHEMA_DESIGNATOR = carrier_schema_designator(
    schema_name="PackageIntegrityAnchor.schema.json"
)


def _require_identifier(*, value: str, label: str) -> None:
    if value == "" or value != value.strip():
        raise PackageIntegrityAnchorError(f"{label} must be exact non-empty text.")
    parsed = urlparse(value)
    if not parsed.scheme:
        raise PackageIntegrityAnchorError(f"{label} must be an absolute URI.")
    if parsed.scheme in {"http", "https"} and not parsed.netloc:
        raise PackageIntegrityAnchorError(
            f"{label} must include an authority for HTTP(S)."
        )


def _require_sha256_designator(
    *,
    designator: ImmutableDesignator,
    label: str,
) -> None:
    if designator.digest.algorithm_id != "sha256":
        raise PackageIntegrityAnchorError(f"{label} must use the sha256 token.")
    try:
        decode_lowercase_hex(
            text=designator.digest.digest_value,
            exact_octets=32,
        )
    except HexEncodingError as exc:
        raise PackageIntegrityAnchorError(f"{label}: {exc}") from exc


@dataclass(frozen=True, slots=True, kw_only=True)
class PackageIntegrityAnchor:
    """Detached signature material preserving both identifier/source pairs."""

    package_identifier: PackageIdentifier
    package_integrity_manifest_member_name: MemberName
    verification_method_identifier: str
    verification_method_designator: ImmutableDesignator
    verification_key_designator: ImmutableDesignator
    verification_key_text: str
    signature_algorithm_identifier: str
    signature_algorithm_designator: ImmutableDesignator
    signature_base64: str

    def __post_init__(self) -> None:
        if str(self.package_identifier) == "":
            raise PackageIntegrityAnchorError("package_identifier must be non-empty.")
        if str(self.package_integrity_manifest_member_name).strip() == "":
            raise PackageIntegrityAnchorError(
                "package_integrity_manifest_member_name must be non-empty."
            )
        _require_identifier(
            value=self.verification_method_identifier,
            label="verification_method_identifier",
        )
        _require_identifier(
            value=self.signature_algorithm_identifier,
            label="signature_algorithm_identifier",
        )
        for label, designator in (
            ("verification_method_designator", self.verification_method_designator),
            ("verification_key_designator", self.verification_key_designator),
            ("signature_algorithm_designator", self.signature_algorithm_designator),
        ):
            _require_sha256_designator(designator=designator, label=label)
        try:
            decode_lowercase_hex(text=self.verification_key_text, exact_octets=32)
        except HexEncodingError as exc:
            raise PackageIntegrityAnchorError(f"verification_key_text: {exc}") from exc
        try:
            decode_canonical_base64(text=self.signature_base64, exact_octets=64)
        except Base64EncodingError as exc:
            raise PackageIntegrityAnchorError(f"signature_base64: {exc}") from exc

    def signature_bytes(self) -> bytes:
        return decode_canonical_base64(
            text=self.signature_base64,
            exact_octets=64,
        )

    def verification_key_bytes(self) -> bytes:
        """Return exact UTF-8 key text bytes bound by the key designator."""

        return self.verification_key_text.encode("utf-8")

    def verification_public_key_bytes(self) -> bytes:
        return decode_lowercase_hex(
            text=self.verification_key_text,
            exact_octets=32,
        )

    def to_json_object(self) -> dict[str, JsonCompatible]:
        return {
            "kind": PACKAGE_INTEGRITY_ANCHOR_KIND,
            "packageIdentifier": str(self.package_identifier),
            "packageIntegrityManifestMember": str(
                self.package_integrity_manifest_member_name
            ),
            "verificationMethodIdentifier": self.verification_method_identifier,
            "verificationMethodDesignator": (
                self.verification_method_designator.to_json_object()
            ),
            "verificationKeyDesignator": (
                self.verification_key_designator.to_json_object()
            ),
            "verificationKeyText": self.verification_key_text,
            "signatureAlgorithmIdentifier": self.signature_algorithm_identifier,
            "signatureAlgorithmDesignator": (
                self.signature_algorithm_designator.to_json_object()
            ),
            "signatureBase64": self.signature_base64,
        }

    def to_json_bytes(self) -> bytes:
        return canonical_json_document_bytes(document=self.to_json_object())


_ANCHOR_FIELDS = frozenset(
    {
        "kind",
        "packageIdentifier",
        "packageIntegrityManifestMember",
        "verificationMethodIdentifier",
        "verificationMethodDesignator",
        "verificationKeyDesignator",
        "verificationKeyText",
        "signatureAlgorithmIdentifier",
        "signatureAlgorithmDesignator",
        "signatureBase64",
    }
)


def _anchor_from_payload(*, payload: Mapping[str, object]) -> PackageIntegrityAnchor:
    require_allowed_keys(
        payload=payload,
        label="package-integrity anchor",
        allowed_keys=_ANCHOR_FIELDS,
        error_type=PackageIntegrityAnchorError,
    )
    if payload.get("kind") != PACKAGE_INTEGRITY_ANCHOR_KIND:
        raise PackageIntegrityAnchorError("package-integrity anchor kind is invalid.")
    return PackageIntegrityAnchor(
        package_identifier=require_package_identifier(
            value=payload.get("packageIdentifier"),
            label="package-integrity anchor.packageIdentifier",
            error_type=PackageIntegrityAnchorError,
        ),
        package_integrity_manifest_member_name=MemberName(
            require_non_empty_text(
                value=payload.get("packageIntegrityManifestMember"),
                label="package-integrity anchor.packageIntegrityManifestMember",
                error_type=PackageIntegrityAnchorError,
            )
        ),
        verification_method_identifier=require_non_empty_text(
            value=payload.get("verificationMethodIdentifier"),
            label="package-integrity anchor.verificationMethodIdentifier",
            error_type=PackageIntegrityAnchorError,
        ),
        verification_method_designator=parse_immutable_designator_object(
            value=payload.get("verificationMethodDesignator"),
            label="package-integrity anchor.verificationMethodDesignator",
            error_type=PackageIntegrityAnchorError,
        ),
        verification_key_designator=parse_immutable_designator_object(
            value=payload.get("verificationKeyDesignator"),
            label="package-integrity anchor.verificationKeyDesignator",
            error_type=PackageIntegrityAnchorError,
        ),
        verification_key_text=require_non_empty_text(
            value=payload.get("verificationKeyText"),
            label="package-integrity anchor.verificationKeyText",
            error_type=PackageIntegrityAnchorError,
        ),
        signature_algorithm_identifier=require_non_empty_text(
            value=payload.get("signatureAlgorithmIdentifier"),
            label="package-integrity anchor.signatureAlgorithmIdentifier",
            error_type=PackageIntegrityAnchorError,
        ),
        signature_algorithm_designator=parse_immutable_designator_object(
            value=payload.get("signatureAlgorithmDesignator"),
            label="package-integrity anchor.signatureAlgorithmDesignator",
            error_type=PackageIntegrityAnchorError,
        ),
        signature_base64=require_non_empty_text(
            value=payload.get("signatureBase64"),
            label="package-integrity anchor.signatureBase64",
            error_type=PackageIntegrityAnchorError,
        ),
    )


def parse_package_integrity_anchor_bootstrap_bytes(
    *, preserved_bytes: bytes
) -> PackageIntegrityAnchor:
    """Parse the bounded lexical anchor surface before method selection."""

    outcome = validate_json_representation(preserved_bytes)
    if not outcome.accepted or not isinstance(outcome.value, dict):
        raise PackageIntegrityAnchorError(
            "package-integrity anchor bootstrap representation rejected at "
            f"{outcome.stage}: {outcome.result_code}."
        )
    return _anchor_from_payload(payload=outcome.value)


def parse_package_integrity_anchor_bytes(
    *,
    preserved_bytes: bytes,
    schema_graph: CarrierSchemaGraph | None = None,
) -> PackageIntegrityAnchor:
    outcome = validate_carrier_json(
        preserved_bytes,
        trusted_role=TrustedJSONRole.PACKAGE_INTEGRITY_ANCHOR,
        schema_graph=schema_graph,
    )
    if not outcome.accepted or not isinstance(outcome.value, dict):
        raise PackageIntegrityAnchorError(
            "package-integrity anchor representation rejected at "
            f"{outcome.stage}: {outcome.result_code}."
        )
    return _anchor_from_payload(payload=outcome.value)
