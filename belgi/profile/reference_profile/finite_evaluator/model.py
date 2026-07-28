"""Semantic objects carried by the Part 4 finite evaluator."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.core import Condition


@dataclass(frozen=True, slots=True, kw_only=True)
class FiniteReviewRecord:
    review_identifier: str
    proposal_identifier: str
    proposed_source_state_identifier: str
    baseline_revision_identifier: str
    baseline_source_state_identifier: str
    decision: str


@dataclass(frozen=True, slots=True, kw_only=True)
class FiniteOpaqueEvidenceSubject:
    media_type: str
    preserved_octets: bytes


@dataclass(frozen=True, slots=True, kw_only=True)
class FiniteEvidenceItem:
    identifier: str
    kind: str
    subject: object
    source_class: str | None
    review: FiniteReviewRecord | None


@dataclass(frozen=True, slots=True, kw_only=True)
class FiniteTrustEntry:
    source_class: str
    boundary_participation: str
    authority_level: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class FiniteEvaluatorDeclaration:
    decisive_evidence_identifier: str | None
    trust_entries: tuple[FiniteTrustEntry, ...]

    def trust_entry(self, *, source_class: str) -> FiniteTrustEntry | None:
        for entry in self.trust_entries:
            if entry.source_class == source_class:
                return entry
        return None


@dataclass(frozen=True, slots=True, kw_only=True)
class FiniteCondition(Condition):
    finite_declaration: FiniteEvaluatorDeclaration
