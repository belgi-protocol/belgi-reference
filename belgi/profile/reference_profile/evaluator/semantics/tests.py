from __future__ import annotations

from typing import TYPE_CHECKING, cast

from belgi.profile.exceptions import ProfileError
from belgi.profile.reference_profile.declarations import OutcomePolicyDeclaration
from belgi.profile.reference_profile.evidence.semantics import (
    unwrap_profile_declaration,
)

from .build import evaluate_outcome_policy

if TYPE_CHECKING:
    from belgi.core import EvidenceState, JudgedObject


__all__ = [
    "satisfies_test_policy",
    "test_policy_sat",
]


def satisfies_test_policy(
    *,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
    condition: object,
) -> bool:
    del judged_object
    declaration = unwrap_profile_declaration(condition, OutcomePolicyDeclaration)
    return evaluate_outcome_policy(
        evidence_state=evidence_state,
        declaration=declaration,
    )


def test_policy_sat(
    judged_object: object,
    evidence_state: object,
    condition: object,
) -> bool:
    try:
        return satisfies_test_policy(
            judged_object=cast("JudgedObject", judged_object),
            evidence_state=cast("EvidenceState", evidence_state),
            condition=condition,
        )
    except (AttributeError, ProfileError, ValueError):
        return False
