from __future__ import annotations

from collections.abc import Mapping


def required_crypto_corpus_text(*, payload: Mapping[str, object], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str):
        raise ValueError(f"Crypto corpus input {field!r} must be text.")
    return value


def lowercase_hex_bytes(*, text: str, allow_empty: bool = False) -> bytes:
    if text == "" and allow_empty:
        return b""
    if len(text) % 2 != 0 or any(
        character not in "0123456789abcdef" for character in text
    ):
        raise ValueError("Crypto corpus byte input must be lowercase hexadecimal.")
    return bytes.fromhex(text)


__all__ = ["lowercase_hex_bytes", "required_crypto_corpus_text"]
