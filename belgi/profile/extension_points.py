from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .exceptions import ExtensionPointError as _ExtensionPointError

__all__ = [
    "ALL_RESERVED_EXTENSION_POINTS",
    "CONDITION_VOCABULARY",
    "ENVIRONMENT_ENVELOPE_VOCABULARY",
    "EVALUATOR_DECLARATION_PARAMETER_VOCABULARY",
    "EVIDENCE_CONDITION_BINDING_KINDS",
    "EVIDENCE_VOCABULARY_AND_EVIDENCE_KINDS",
    "GOVERNING_SPECIFICATION_REFERENCE_VOCABULARY",
    "JUDGED_OBJECT_CARRIER_VOCABULARY_AND_CONSTRAINTS",
    "REPLAY_POLICY_REFINEMENTS",
    "REPRESENTATION_SPECIFIC_SCHEMAS_AND_SERIALIZATION_BINDINGS",
    "TRUST_BOUNDARY_VOCABULARY",
    "ReservedExtensionPoint",
    "normalize_extension_points",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReservedExtensionPoint:
    clause: str
    title: str

    def __post_init__(self) -> None:
        if not self.clause.startswith("8."):
            raise _ExtensionPointError(
                "BELGI Part 3 extension-point clauses must start with '8.': "
                f"{self.clause!r}."
            )
        if not self.title.strip():
            raise _ExtensionPointError("extension-point titles must not be empty.")


JUDGED_OBJECT_CARRIER_VOCABULARY_AND_CONSTRAINTS = ReservedExtensionPoint(
    clause="8.2",
    title="judged-object carrier vocabulary and constraints",
)
EVIDENCE_VOCABULARY_AND_EVIDENCE_KINDS = ReservedExtensionPoint(
    clause="8.3",
    title="evidence vocabulary and evidence kinds",
)
CONDITION_VOCABULARY = ReservedExtensionPoint(
    clause="8.4",
    title="condition vocabulary",
)
TRUST_BOUNDARY_VOCABULARY = ReservedExtensionPoint(
    clause="8.5",
    title="trust-boundary vocabulary",
)
GOVERNING_SPECIFICATION_REFERENCE_VOCABULARY = ReservedExtensionPoint(
    clause="8.6",
    title="governing-specification reference vocabulary",
)
EVIDENCE_CONDITION_BINDING_KINDS = ReservedExtensionPoint(
    clause="8.7",
    title="evidence-condition binding kinds",
)
ENVIRONMENT_ENVELOPE_VOCABULARY = ReservedExtensionPoint(
    clause="8.8",
    title="environment-envelope vocabulary",
)
EVALUATOR_DECLARATION_PARAMETER_VOCABULARY = ReservedExtensionPoint(
    clause="8.9",
    title="evaluator declaration parameter vocabulary",
)
REPLAY_POLICY_REFINEMENTS = ReservedExtensionPoint(
    clause="8.10",
    title="replay-policy refinements",
)
REPRESENTATION_SPECIFIC_SCHEMAS_AND_SERIALIZATION_BINDINGS = ReservedExtensionPoint(
    clause="8.11",
    title="representation-specific schemas and serialization bindings",
)

ALL_RESERVED_EXTENSION_POINTS: tuple[ReservedExtensionPoint, ...] = (
    JUDGED_OBJECT_CARRIER_VOCABULARY_AND_CONSTRAINTS,
    EVIDENCE_VOCABULARY_AND_EVIDENCE_KINDS,
    CONDITION_VOCABULARY,
    TRUST_BOUNDARY_VOCABULARY,
    GOVERNING_SPECIFICATION_REFERENCE_VOCABULARY,
    EVIDENCE_CONDITION_BINDING_KINDS,
    ENVIRONMENT_ENVELOPE_VOCABULARY,
    EVALUATOR_DECLARATION_PARAMETER_VOCABULARY,
    REPLAY_POLICY_REFINEMENTS,
    REPRESENTATION_SPECIFIC_SCHEMAS_AND_SERIALIZATION_BINDINGS,
)


def normalize_extension_points(
    *,
    points: Iterable[ReservedExtensionPoint],
) -> tuple[ReservedExtensionPoint, ...]:
    reserved_by_clause = {
        point.clause: point for point in ALL_RESERVED_EXTENSION_POINTS
    }
    normalized: list[ReservedExtensionPoint] = []
    seen: set[str] = set()
    for point in points:
        reserved = reserved_by_clause.get(point.clause)
        if reserved is None or reserved.title != point.title:
            raise _ExtensionPointError(
                "only BELGI Part 3 reserved extension points from clauses 8.2 to 8.11 "
                "may be used."
            )
        if point.clause in seen:
            continue
        normalized.append(reserved)
        seen.add(point.clause)
    return tuple(normalized)
