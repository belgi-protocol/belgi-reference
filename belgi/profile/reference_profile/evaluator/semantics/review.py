from __future__ import annotations

from typing import TYPE_CHECKING, cast

from belgi.profile.exceptions import ProfileError
from belgi.profile.reference_profile.declarations import ReviewPolicyDeclaration
from belgi.profile.reference_profile.evidence.semantics import (
    bound_evidence_items,
    unwrap_profile_declaration,
)
from belgi.profile.reference_profile.evidence.subject_access import subject_field

if TYPE_CHECKING:
    from belgi.core import EvidenceState, JudgedObject


__all__ = [
    "review_policy_sat",
    "satisfies_review_policy",
]


def _approval_count(item: object) -> int | None:
    for field_name in ("approval_count", "approvals", "approver_count"):
        value = subject_field(item, field_name)
        if isinstance(value, int):
            return value
    return None


def _blocking_count(item: object) -> int | None:
    for field_name in ("blocking_count", "blocking_reviews", "requested_changes"):
        value = subject_field(item, field_name)
        if isinstance(value, bool):
            return 1 if value else 0
        if isinstance(value, int):
            return value
    return None


def satisfies_review_policy(
    *,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
    condition: object,
) -> bool:
    del judged_object
    declaration = unwrap_profile_declaration(condition, ReviewPolicyDeclaration)
    total_approvals = 0
    total_blocking = 0
    for binding in declaration.required_bindings:
        items = bound_evidence_items(
            evidence_state=evidence_state,
            binding=binding,
            condition=declaration,
        )
        if len(items) < binding.minimum_count:
            return False
        for item in items:
            approvals = _approval_count(item)
            blocking = _blocking_count(item)
            if approvals is None and blocking is None:
                return False
            total_approvals += approvals or 0
            total_blocking += blocking or 0
    if total_approvals < declaration.minimum_approvals:
        return False
    if not declaration.allow_blocking_reviews and total_blocking > 0:
        return False
    return True


def review_policy_sat(
    judged_object: object,
    evidence_state: object,
    condition: object,
) -> bool:
    try:
        return satisfies_review_policy(
            judged_object=cast("JudgedObject", judged_object),
            evidence_state=cast("EvidenceState", evidence_state),
            condition=condition,
        )
    except (AttributeError, ProfileError, ValueError):
        return False
