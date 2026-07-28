from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "ReferenceProfileEvidenceItem",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileEvidenceItem:
    identifier: str
    kind: str
    subject: object
    source_class: str | None
    boundary_participation: str | None
    authority_level: str | None
    outcome: str | None = None
    numeric_value: float | None = None
    severity: str | None = None
    failure_count: int | None = None
    approval_count: int | None = None
    blocking_count: int | None = None
    environment_terms: dict[str, object] | None = None
    equivalence_basis: str | None = None
