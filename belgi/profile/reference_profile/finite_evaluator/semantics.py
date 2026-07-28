"""Total Part 4 finite condition semantics over induced J and E."""

from __future__ import annotations

from belgi.core import EvidenceState, JudgedObject
from belgi.profile.reference_profile.declarations.source import REVIEW_SYSTEM_SOURCE
from belgi.profile.reference_profile.evidence.subject_access import (
    subject_mapping_view,
)
from belgi.profile.reference_profile.identifiers.authority import AUTHORITATIVE
from belgi.profile.reference_profile.identifiers.boundary import INCLUDED
from belgi.profile.reference_profile.identifiers.evidence_kinds import REVIEW_RECORD

from .model import FiniteCondition, FiniteEvidenceItem


def finite_required_evidence_present_sat(
    *, judged: object, evidence: EvidenceState, condition: object
) -> bool:
    del judged
    return _required_review(evidence=evidence, condition=condition) is not None


def change_basis_resolved_sat(
    *, judged: object, evidence: EvidenceState, condition: object
) -> bool:
    review_item = _required_review(evidence=evidence, condition=condition)
    identities = _judged_identities(judged)
    if review_item is None or review_item.review is None or identities is None:
        return False
    review = review_item.review
    return (
        review.proposal_identifier == identities[0]
        and review.proposed_source_state_identifier == identities[1]
        and review.baseline_revision_identifier == identities[2]
        and review.baseline_source_state_identifier == identities[3]
    )


def review_policy_satisfied_sat(
    *, judged: object, evidence: EvidenceState, condition: object
) -> bool:
    del judged
    review_item = _required_review(evidence=evidence, condition=condition)
    return (
        review_item is not None
        and review_item.review is not None
        and review_item.review.decision == "accepted"
    )


def _required_review(
    *, evidence: EvidenceState, condition: object
) -> FiniteEvidenceItem | None:
    if not isinstance(condition, FiniteCondition):
        return None
    declaration = condition.finite_declaration
    identifier = declaration.decisive_evidence_identifier
    if identifier is None:
        return None
    item = next(
        (
            candidate
            for candidate in evidence.items
            if isinstance(candidate, FiniteEvidenceItem)
            and candidate.identifier == identifier
        ),
        None,
    )
    source_class = None if item is None else item.source_class
    if (
        item is None
        or item.kind != REVIEW_RECORD
        or item.review is None
        or not isinstance(source_class, str)
        or source_class != REVIEW_SYSTEM_SOURCE
    ):
        return None
    trust = declaration.trust_entry(source_class=source_class)
    if (
        trust is None
        or trust.boundary_participation != INCLUDED
        or trust.authority_level != AUTHORITATIVE
    ):
        return None
    return item


def _judged_identities(value: object) -> tuple[str, str, str, str] | None:
    if not isinstance(value, JudgedObject):
        return None
    proposal = value.admission_subject.value
    baseline = value.reference_context.value
    proposal_mapping = subject_mapping_view(proposal)
    baseline_mapping = subject_mapping_view(baseline)
    if proposal_mapping is None or baseline_mapping is None:
        return None
    proposal_identifier = proposal_mapping.get("proposalIdentifier")
    proposed_source_state_identifier = proposal_mapping.get(
        "proposedSourceStateIdentifier"
    )
    baseline_revision_identifier = baseline_mapping.get("baselineRevisionIdentifier")
    baseline_source_state_identifier = baseline_mapping.get(
        "baselineSourceStateIdentifier"
    )
    if not isinstance(proposal_identifier, str) or not proposal_identifier:
        return None
    if (
        not isinstance(proposed_source_state_identifier, str)
        or not proposed_source_state_identifier
    ):
        return None
    if (
        not isinstance(baseline_revision_identifier, str)
        or not baseline_revision_identifier
    ):
        return None
    if (
        not isinstance(baseline_source_state_identifier, str)
        or not baseline_source_state_identifier
    ):
        return None
    return (
        proposal_identifier,
        proposed_source_state_identifier,
        baseline_revision_identifier,
        baseline_source_state_identifier,
    )
