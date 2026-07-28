from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier import (
    ConditionIdentifier,
    EvaluatorCarrier,
    EvidenceConditionBindingDeclaration,
    EvidenceIdentifier,
    EvidenceKindIdentifier,
    EvidenceStateCarrier,
)

__all__ = [
    "ConditionEvidenceBindingMatch",
    "MatchedEvidenceItem",
    "resolve_evidence_condition_bindings",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class MatchedEvidenceItem:
    evidence_identifier: EvidenceIdentifier
    evidence_kind_identifier: EvidenceKindIdentifier


@dataclass(frozen=True, slots=True, kw_only=True)
class ConditionEvidenceBindingMatch:
    condition_identifier: ConditionIdentifier
    binding: EvidenceConditionBindingDeclaration
    matched_evidence: tuple[MatchedEvidenceItem, ...]

    @property
    def match_count(self) -> int:
        return len(self.matched_evidence)


def resolve_evidence_condition_bindings(
    *,
    evidence_state_carrier: EvidenceStateCarrier,
    evaluator_carrier: EvaluatorCarrier,
) -> tuple[ConditionEvidenceBindingMatch, ...]:
    evidence_items_by_identifier = {
        evidence_item.evidence_identifier: evidence_item
        for evidence_item in evidence_state_carrier.evidence_items
    }
    matches: list[ConditionEvidenceBindingMatch] = []
    for binding in evaluator_carrier.evidence_condition_bindings:
        matched_evidence: list[MatchedEvidenceItem] = []
        for evidence_identifier in binding.evidence_identifiers:
            evidence_item = evidence_items_by_identifier.get(evidence_identifier)
            if evidence_item is None:
                continue
            matched_evidence.append(
                MatchedEvidenceItem(
                    evidence_identifier=evidence_item.evidence_identifier,
                    evidence_kind_identifier=evidence_item.evidence_kind_identifier,
                )
            )
        matches.append(
            ConditionEvidenceBindingMatch(
                condition_identifier=binding.condition_identifier,
                binding=binding,
                matched_evidence=tuple(matched_evidence),
            )
        )
    return tuple(matches)
