from __future__ import annotations


class BelgiSubstrateError(Exception):
    """Base exception for substrate-owned failures."""


class Base64EncodingError(BelgiSubstrateError, ValueError):
    """Raised when text is not standard padded Base64."""


class Base64LengthError(Base64EncodingError):
    """Raised when decoded Base64 has the wrong exact size."""


class NonCanonicalBase64Error(Base64EncodingError):
    """Raised when Base64 text does not use the canonical RFC 4648 spelling."""


class HexEncodingError(BelgiSubstrateError, ValueError):
    """Raised when text is not lowercase hexadecimal."""


class HexLengthError(HexEncodingError):
    """Raised when decoded hexadecimal has the wrong exact size."""


class CryptoDependencyError(BelgiSubstrateError):
    """Raised when required crypto support is unavailable at runtime."""


class Ed25519KeyError(BelgiSubstrateError):
    """Raised when an Ed25519 key blob cannot be loaded or is invalid."""


class Ed25519PointEncodingError(Ed25519KeyError):
    """Raised when compressed Edwards-point bytes are not canonical."""


class Ed25519PointOrderError(Ed25519KeyError):
    """Raised when an Ed25519 public key does not have exact order L."""


class Ed25519SignatureError(BelgiSubstrateError):
    """Raised when Ed25519 signing or verification fails."""


class Ed25519SignatureEncodingError(Ed25519SignatureError):
    """Raised when an Ed25519 signature has an invalid encoding."""


class Ed25519ScalarEncodingError(Ed25519SignatureEncodingError):
    """Raised when an Ed25519 signature scalar is not canonical."""


class YamlParseError(BelgiSubstrateError):
    """Raised when deterministic YAML subset parsing fails."""


__all__ = [
    "Base64EncodingError",
    "Base64LengthError",
    "BelgiSubstrateError",
    "CryptoDependencyError",
    "Ed25519KeyError",
    "Ed25519PointEncodingError",
    "Ed25519PointOrderError",
    "Ed25519ScalarEncodingError",
    "Ed25519SignatureEncodingError",
    "Ed25519SignatureError",
    "HexEncodingError",
    "HexLengthError",
    "NonCanonicalBase64Error",
    "YamlParseError",
]
