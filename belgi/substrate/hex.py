from __future__ import annotations

from .exceptions import HexEncodingError, HexLengthError


def decode_lowercase_hex(*, text: str, exact_octets: int) -> bytes:
    """Decode exact-length lowercase hexadecimal without normalization."""

    if not isinstance(text, str):
        raise HexEncodingError("Hexadecimal value must be text.")
    if len(text) != exact_octets * 2:
        raise HexLengthError(
            f"Hexadecimal value must encode exactly {exact_octets} octets."
        )
    if any(character not in "0123456789abcdef" for character in text):
        raise HexEncodingError(
            "Hexadecimal value must contain lowercase ASCII hexadecimal only."
        )
    return bytes.fromhex(text)


def encode_lowercase_hex(*, payload: bytes) -> str:
    return payload.hex()


__all__ = [
    "decode_lowercase_hex",
    "encode_lowercase_hex",
]
