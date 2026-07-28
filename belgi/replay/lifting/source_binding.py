from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier import (
    ImmutableDesignator,
    ReferencedSourceBinding,
    ReferencedSourceKind,
)
from belgi.substrate.hash import sha256_bytes

__all__ = [
    "VerifiedReferencedSource",
    "validate_referenced_source_bytes",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class VerifiedReferencedSource:
    source_kind: ReferencedSourceKind
    immutable_designator: ImmutableDesignator


def validate_referenced_source_bytes(
    *,
    preserved_bytes: bytes,
    binding: ReferencedSourceBinding,
    description: str,
) -> VerifiedReferencedSource:
    digest = binding.designator.digest
    if digest.algorithm_id != "sha256":
        raise ValueError(
            f"{description} uses unsupported exact-edition digest algorithm "
            f"{digest.algorithm_id!r}."
        )
    observed_digest = sha256_bytes(preserved_bytes)
    if observed_digest != digest.digest_value:
        raise ValueError(
            f"{description} bytes do not match the claim-record exact-edition "
            "designator."
        )
    return VerifiedReferencedSource(
        source_kind=binding.source_kind,
        immutable_designator=binding.designator,
    )
