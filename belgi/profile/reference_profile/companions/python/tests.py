from __future__ import annotations

from typing import TYPE_CHECKING, cast

from belgi.profile.companions.python.identifiers.params import ANALYSIS_SCOPE_PARAMETER
from belgi.profile.exceptions import ProfileError
from belgi.profile.reference_profile.declarations import OutcomePolicyDeclaration
from belgi.profile.reference_profile.evaluator.semantics.tests import (
    satisfies_test_policy,
)
from belgi.profile.reference_profile.evidence.semantics import (
    bound_evidence_items,
    unwrap_profile_declaration,
)
from belgi.profile.reference_profile.evidence.subject_access import subject_from_item

if TYPE_CHECKING:
    from belgi.core import EvidenceState, JudgedObject

__all__ = ["python_tests_pass_sat", "satisfies_python_tests_pass"]


def _analysis_scope_present(*, item: object) -> bool:
    subject = subject_from_item(item)
    if subject is None:
        return False
    value = subject.get(str(ANALYSIS_SCOPE_PARAMETER))
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple)):
        return bool(value)
    return False


def satisfies_python_tests_pass(
    *,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
    condition: object,
) -> bool:
    declaration = unwrap_profile_declaration(
        condition,
        OutcomePolicyDeclaration,
    )
    for binding in declaration.required_bindings:
        items = bound_evidence_items(
            evidence_state=evidence_state,
            binding=binding,
            condition=declaration,
        )
        if len(items) < binding.minimum_count:
            return False
        if any(not _analysis_scope_present(item=item) for item in items):
            return False
    return satisfies_test_policy(
        judged_object=judged_object,
        evidence_state=evidence_state,
        condition=declaration,
    )


def python_tests_pass_sat(
    judged_object: object,
    evidence_state: object,
    condition: object,
) -> bool:
    try:
        return satisfies_python_tests_pass(
            judged_object=cast("JudgedObject", judged_object),
            evidence_state=cast("EvidenceState", evidence_state),
            condition=condition,
        )
    except (AttributeError, ProfileError, TypeError, ValueError):
        return False
