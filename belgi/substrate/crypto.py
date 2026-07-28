from __future__ import annotations

from typing import Any

from .ed25519_acceptance import (
    decode_canonical_point,
    has_exact_group_order,
    observe_ed25519_acceptance,
)
from .exceptions import (
    CryptoDependencyError,
    Ed25519KeyError,
    Ed25519PointEncodingError,
    Ed25519PointOrderError,
    Ed25519ScalarEncodingError,
    Ed25519SignatureEncodingError,
    Ed25519SignatureError,
    HexEncodingError,
)
from .hex import decode_lowercase_hex

_ED25519_GROUP_ORDER = 2**252 + 27742317777372353535851937790883648493


def _cryptography_ed25519_public_key_type() -> type[Any]:
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PublicKey,
        )
    except Exception as exc:  # pragma: no cover - dependency gate owns this path
        raise CryptoDependencyError(
            "Missing declared cryptography support for pure Ed25519."
        ) from exc
    return Ed25519PublicKey


def load_ed25519_public_key(blob: bytes) -> Any:
    """Load one canonical raw 32-octet Ed25519 public key."""

    if len(blob) != 32:
        raise Ed25519KeyError("Ed25519 public key must contain exactly 32 octets.")
    point = decode_canonical_point(blob)
    if point is None:
        raise Ed25519PointEncodingError(
            "Ed25519 public key is not a canonical compressed Edwards point."
        )
    if not has_exact_group_order(point):
        raise Ed25519PointOrderError(
            "Ed25519 public key must be a non-identity point of exact order L."
        )
    public_key_type = _cryptography_ed25519_public_key_type()
    try:
        return public_key_type.from_public_bytes(blob)
    except Exception as exc:
        raise Ed25519KeyError("Ed25519 public key is invalid.") from exc


def parse_ed25519_public_key_hex(public_key_hex: str) -> Any:
    try:
        public_key_bytes = decode_lowercase_hex(
            text=public_key_hex,
            exact_octets=32,
        )
    except HexEncodingError as exc:
        raise Ed25519KeyError(
            "Ed25519 public key must use exact lowercase 32-octet hexadecimal."
        ) from exc
    return load_ed25519_public_key(public_key_bytes)


def require_pure_ed25519_signature(signature: bytes) -> None:
    if len(signature) != 64:
        raise Ed25519SignatureEncodingError(
            "Ed25519 signature must contain exactly 64 octets."
        )
    if decode_canonical_point(signature[:32]) is None:
        raise Ed25519SignatureEncodingError(
            "Ed25519 signature R is not a canonical compressed Edwards point."
        )
    scalar = int.from_bytes(signature[32:], "little")
    if scalar >= _ED25519_GROUP_ORDER:
        raise Ed25519ScalarEncodingError("Ed25519 signature scalar S is not canonical.")


def verify_ed25519_signature(
    public_key: Any,
    signature: bytes,
    payload: bytes,
    *,
    context: str,
) -> None:
    require_pure_ed25519_signature(signature)
    try:
        public_key_bytes = public_key.public_bytes_raw()
    except Exception as exc:
        raise Ed25519KeyError("Ed25519 public key cannot expose raw bytes.") from exc
    observation = observe_ed25519_acceptance(
        public_key=public_key_bytes,
        message=payload,
        signature=signature,
    )
    if not observation.public_key_exact_order:
        raise Ed25519PointOrderError(
            "Ed25519 public key must be a non-identity point of exact order L."
        )
    if not observation.accepted:
        raise Ed25519SignatureError(f"Invalid pure Ed25519 signature ({context}).")
    try:
        public_key.verify(signature, payload)
    except Exception as exc:
        raise Ed25519SignatureError(
            f"Invalid pure Ed25519 signature ({context})."
        ) from exc


__all__ = [
    "load_ed25519_public_key",
    "parse_ed25519_public_key_hex",
    "require_pure_ed25519_signature",
    "verify_ed25519_signature",
]
