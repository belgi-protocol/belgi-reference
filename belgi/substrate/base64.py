from __future__ import annotations

import base64
import binascii

from .exceptions import (
    Base64EncodingError,
    Base64LengthError,
    NonCanonicalBase64Error,
)


def decode_canonical_base64(*, text: str, exact_octets: int) -> bytes:
    """Decode one exact-length canonical RFC 4648 Base64 value."""

    if not isinstance(text, str):
        raise Base64EncodingError("Base64 value must be text.")
    try:
        encoded = text.encode("ascii", errors="strict")
    except UnicodeEncodeError as exc:
        raise Base64EncodingError(
            "Base64 value must contain only the standard ASCII alphabet."
        ) from exc
    try:
        decoded = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise Base64EncodingError(
            "Base64 value must use the standard alphabet and required padding."
        ) from exc
    if len(decoded) != exact_octets:
        raise Base64LengthError(
            f"Base64 value must decode to exactly {exact_octets} octets."
        )
    if base64.b64encode(decoded) != encoded:
        raise NonCanonicalBase64Error("Base64 value is not canonically encoded.")
    return decoded


def encode_canonical_base64(*, payload: bytes) -> str:
    """Encode bytes using canonical padded RFC 4648 Base64."""

    return base64.b64encode(payload).decode("ascii")


__all__ = [
    "decode_canonical_base64",
    "encode_canonical_base64",
]
