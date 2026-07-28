"""Producer-side integrity binding construction."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse

from belgi.carrier.exceptions import (
    IntegrityError,
    UnsupportedCanonicalizationError,
    UnsupportedIntegrityAlgorithmError,
)
from belgi.carrier.inventory import CanonicalReference, ImmutableDesignator
from belgi.carrier.projection import ProjectionResult
from belgi.substrate.hash import sha256_bytes
from belgi.substrate.io import canonical_json_text

__all__ = [
    "BoundObjectKind",
    "IntegrityBinding",
    "IntegrityPolicy",
    "build_integrity_binding",
    "canonical_json_document_bytes",
]


class BoundObjectKind(str, Enum):
    """Which byte sequence an integrity binding covers."""

    EXACT_PRESERVED_OCTETS = "exact-preserved-octets"
    CANONICAL_PROJECTION = "canonical-projection"


def canonical_json_document_bytes(*, document: object) -> bytes:
    """Serialize a JSON-compatible document deterministically."""

    try:
        return canonical_json_text(document).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise UnsupportedCanonicalizationError(
            "Document cannot be serialized as deterministic JSON."
        ) from exc


@dataclass(frozen=True, slots=True, kw_only=True)
class IntegrityPolicy:
    """Producer-side policy for constructing member integrity bindings."""

    algorithm_identifier: str
    algorithm_designator: ImmutableDesignator
    bound_object: BoundObjectKind
    canonicalization_rule_identifier: str | None = None
    canonicalization_rule_designator: ImmutableDesignator | None = None

    def __post_init__(self) -> None:
        raise UnsupportedIntegrityAlgorithmError(
            "Integrity policies require a source-verified construction path."
        )

    def _validate_shape(self) -> None:
        _require_absolute_identifier(
            self.algorithm_identifier,
            label="algorithm_identifier",
        )
        if self.bound_object == BoundObjectKind.EXACT_PRESERVED_OCTETS:
            if (
                self.canonicalization_rule_identifier is not None
                or self.canonicalization_rule_designator is not None
            ):
                raise IntegrityError(
                    "Exact-octet bindings shall not identify a canonicalization rule."
                )
            return
        if self.bound_object == BoundObjectKind.CANONICAL_PROJECTION:
            if (
                self.canonicalization_rule_identifier is None
                or self.canonicalization_rule_designator is None
            ):
                raise IntegrityError(
                    "Canonical-projection bindings require an explicit canonicalization rule designator."
                )
            return
        raise IntegrityError(f"Unsupported bound object kind: {self.bound_object!r}")

    @classmethod
    def exact_octets_sha256_from_verified_source(
        cls,
        *,
        algorithm_identifier: str,
        algorithm_designator: ImmutableDesignator,
    ) -> IntegrityPolicy:
        """Construct after an upstream owner verifies the exact source bytes."""

        return _SourceVerifiedSha256IntegrityPolicy(
            algorithm_identifier=algorithm_identifier,
            algorithm_designator=algorithm_designator,
            bound_object=BoundObjectKind.EXACT_PRESERVED_OCTETS,
            canonicalization_rule_identifier=None,
            canonicalization_rule_designator=None,
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class _SourceVerifiedSha256IntegrityPolicy(IntegrityPolicy):
    """SHA-256 policy whose designator was verified by a profile owner."""

    def __post_init__(self) -> None:
        self._validate_shape()


@dataclass(frozen=True, slots=True, kw_only=True)
class IntegrityBinding:
    """Integrity binding preserved inside the package-integrity manifest."""

    member_reference: CanonicalReference
    algorithm_identifier: str
    algorithm_designator: ImmutableDesignator
    bound_object: BoundObjectKind
    bound_value_hex: str
    canonicalization_rule_identifier: str | None = None
    canonicalization_rule_designator: ImmutableDesignator | None = None

    def __post_init__(self) -> None:
        _require_absolute_identifier(
            self.algorithm_identifier,
            label="algorithm_identifier",
        )
        if self.bound_object == BoundObjectKind.EXACT_PRESERVED_OCTETS:
            if (
                self.canonicalization_rule_identifier is not None
                or self.canonicalization_rule_designator is not None
            ):
                raise IntegrityError(
                    "Exact-octet integrity bindings shall not include canonicalization identifiers."
                )
            return
        if self.bound_object == BoundObjectKind.CANONICAL_PROJECTION:
            if (
                self.canonicalization_rule_identifier is None
                or self.canonicalization_rule_designator is None
            ):
                raise IntegrityError(
                    "Canonical-projection bindings require canonicalization identifiers."
                )
            return
        raise IntegrityError(f"Unsupported bound object kind: {self.bound_object!r}")


def _require_absolute_identifier(value: str, *, label: str) -> None:
    if not isinstance(value, str) or not value or value != value.strip():
        raise IntegrityError(f"{label} must be exact non-empty text.")
    parsed = urlparse(value)
    if not parsed.scheme or parsed.fragment:
        raise IntegrityError(f"{label} must be an absolute URI without a fragment.")


def build_integrity_binding(
    *,
    member_reference: CanonicalReference,
    preserved_bytes: bytes,
    projection: ProjectionResult,
    integrity_policy: IntegrityPolicy,
) -> IntegrityBinding:
    """Construct one integrity binding for a replay-relevant package member."""

    del projection
    if not isinstance(integrity_policy, _SourceVerifiedSha256IntegrityPolicy):
        raise UnsupportedIntegrityAlgorithmError(
            "Integrity binding construction requires a source-verified policy."
        )
    if integrity_policy.bound_object is not BoundObjectKind.EXACT_PRESERVED_OCTETS:
        raise UnsupportedCanonicalizationError(
            "This implementation does not claim a canonical-projection integrity policy."
        )

    return IntegrityBinding(
        member_reference=member_reference,
        algorithm_identifier=integrity_policy.algorithm_identifier,
        algorithm_designator=integrity_policy.algorithm_designator,
        bound_object=integrity_policy.bound_object,
        bound_value_hex=sha256_bytes(preserved_bytes).lower(),
        canonicalization_rule_identifier=(
            integrity_policy.canonicalization_rule_identifier
        ),
        canonicalization_rule_designator=integrity_policy.canonicalization_rule_designator,
    )
