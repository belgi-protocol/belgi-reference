from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha512_bytes(data: bytes) -> bytes:
    return hashlib.sha512(data).digest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_copy_stream(source: BinaryIO, destination: BinaryIO) -> str:
    """Copy a binary stream while returning the copied bytes' SHA-256."""
    h = hashlib.sha256()
    for chunk in iter(lambda: source.read(1024 * 1024), b""):
        destination.write(chunk)
        h.update(chunk)
    return h.hexdigest()


def sha256_stream(source: BinaryIO) -> str:
    """Return the SHA-256 of bytes read from a binary stream."""
    h = hashlib.sha256()
    for chunk in iter(lambda: source.read(1024 * 1024), b""):
        h.update(chunk)
    return h.hexdigest()


def is_hex_sha256(s: str) -> bool:
    if not isinstance(s, str) or len(s) != 64:
        return False
    for c in s:
        if c not in "0123456789abcdefABCDEF":
            return False
    return True


__all__ = [
    "is_hex_sha256",
    "sha256_bytes",
    "sha256_copy_stream",
    "sha256_file",
    "sha256_stream",
    "sha256_text",
    "sha512_bytes",
]
