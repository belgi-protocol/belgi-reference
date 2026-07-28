"""Machine-readable bounded companion support statements."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from belgi.profile.edition import ExactEditionBinding
from belgi.profile.source_material import ProfileExactEditionSource
from belgi.substrate.hash import sha256_bytes
from belgi.substrate.time import UtcDate

__all__ = [
    "CompanionSupportStatement",
    "SupportDirection",
    "SupportStatus",
    "SupportedIdentifier",
    "require_exact_companion_source",
]


class SupportDirection(str, Enum):
    PRODUCER = "producer"
    VERIFIER = "verifier"


class SupportStatus(str, Enum):
    CONFORMANCE = "conformance"
    DIAGNOSTIC = "diagnostic"


@dataclass(frozen=True, slots=True, kw_only=True)
class SupportedIdentifier:
    vocabulary: str
    identifier: str
    directions: tuple[SupportDirection, ...]

    def __post_init__(self) -> None:
        if not self.vocabulary or not self.identifier:
            raise ValueError(
                "supported identifier vocabulary and identifier are required."
            )
        if not self.directions:
            raise ValueError("supported identifier directions must not be empty.")
        if len(set(self.directions)) != len(self.directions):
            raise ValueError("supported identifier directions must be unique.")

    def to_document(self) -> dict[str, object]:
        return {
            "vocabulary": self.vocabulary,
            "identifier": self.identifier,
            "supportDirections": [direction.value for direction in self.directions],
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class CompanionSupportStatement:
    implementation_identifier: str
    document_title: str
    conformance_class: str
    status: SupportStatus
    companion_source: ProfileExactEditionSource
    supported_identifiers: tuple[SupportedIdentifier, ...]
    statement_date: UtcDate

    def __post_init__(self) -> None:
        if not self.implementation_identifier or not self.document_title:
            raise ValueError(
                "support statement implementation and document are required."
            )
        if not self.conformance_class:
            raise ValueError("support statement conformance class is required.")
        if "Full" in self.conformance_class:
            raise ValueError("bounded support statements must not claim a Full class.")
        if not self.supported_identifiers:
            raise ValueError("support statement identifiers must not be empty.")
        identifiers = tuple(
            (entry.vocabulary, entry.identifier) for entry in self.supported_identifiers
        )
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("support statement identifiers must be unique.")
        require_exact_companion_source(source=self.companion_source)

    def to_document(self) -> dict[str, object]:
        binding = self.companion_source.binding
        designator = binding.immutable_designator
        return {
            "implementationIdentifier": self.implementation_identifier,
            "documentTitle": self.document_title,
            "documentVersion": str(binding.version_designator),
            "conformanceClass": self.conformance_class,
            "status": self.status.value,
            "companionIdentifier": str(binding.family_identifier),
            "exactEdition": {
                "kind": binding.kind.value,
                "immutableDesignator": {
                    "uri": designator.uri,
                    "digest": {
                        "algorithmId": designator.digest.algorithm_id,
                        "digestValue": designator.digest.digest_value,
                    },
                },
            },
            "supportedIdentifiers": [
                entry.to_document() for entry in self.supported_identifiers
            ],
            "statementDate": self.statement_date.isoformat(),
        }


def require_exact_companion_source(
    *,
    source: ProfileExactEditionSource,
    expected_binding: ExactEditionBinding | None = None,
) -> None:
    binding = source.binding
    if expected_binding is not None and binding != expected_binding:
        raise ValueError(
            "companion support source does not match the selected binding."
        )
    designator = binding.immutable_designator
    if designator.digest.algorithm_id != "sha256":
        raise ValueError("companion support source must use the exact sha256 token.")
    if sha256_bytes(source.preserved_bytes) != designator.digest.digest_value:
        raise ValueError("companion support source bytes do not match its designator.")
