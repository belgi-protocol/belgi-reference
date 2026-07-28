from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from belgi.substrate.exceptions import HexEncodingError
from belgi.substrate.hash import sha256_bytes
from belgi.substrate.hex import decode_lowercase_hex

from .constants import DESIGNATOR_DIGEST_ALGORITHM_TOKEN
from .exceptions import (
    SourceDigestMismatchError,
    SourceDigestTextError,
    SourceIdentifierMismatchError,
)


class _DigestSurface(Protocol):
    @property
    def algorithm_id(self) -> str: ...

    @property
    def digest_value(self) -> str: ...


class DesignatorSurface(Protocol):
    @property
    def uri(self) -> str: ...

    @property
    def digest(self) -> _DigestSurface: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class ExactSourceBinding:
    uri: str
    sha256: str

    def matches(self, *, designator: DesignatorSurface) -> bool:
        return (
            designator.uri == self.uri
            and designator.digest.algorithm_id == DESIGNATOR_DIGEST_ALGORITHM_TOKEN
            and designator.digest.digest_value == self.sha256
        )


def require_identified_exact_source(
    *,
    requested_identifier: str,
    designated_identifier: str,
    source_uri: str,
    source_bytes: bytes,
    digest_algorithm_id: str,
    digest_hex: str,
) -> ExactSourceBinding:
    """Validate one identified source against its exact supplied octets."""

    if requested_identifier != designated_identifier:
        raise SourceIdentifierMismatchError(
            "Requested and designated stable identifiers must match exactly."
        )
    if digest_algorithm_id != DESIGNATOR_DIGEST_ALGORITHM_TOKEN:
        raise SourceDigestTextError(
            "Defining-source designator must use the exact sha256 token."
        )
    try:
        decode_lowercase_hex(text=digest_hex, exact_octets=32)
    except HexEncodingError as exc:
        raise SourceDigestTextError(
            "Defining-source digest must be exact lowercase 32-octet hexadecimal."
        ) from exc
    if sha256_bytes(source_bytes) != digest_hex:
        raise SourceDigestMismatchError(
            "Defining-source digest does not bind the exact supplied source bytes."
        )
    return ExactSourceBinding(uri=source_uri, sha256=digest_hex)


def exact_source_binding_from_designator(
    *,
    identifier: str,
    designator: DesignatorSurface,
    source_bytes: bytes,
) -> ExactSourceBinding:
    return require_identified_exact_source(
        requested_identifier=identifier,
        designated_identifier=identifier,
        source_uri=designator.uri,
        source_bytes=source_bytes,
        digest_algorithm_id=designator.digest.algorithm_id,
        digest_hex=designator.digest.digest_value,
    )


__all__ = [
    "DesignatorSurface",
    "ExactSourceBinding",
    "exact_source_binding_from_designator",
    "require_identified_exact_source",
]
