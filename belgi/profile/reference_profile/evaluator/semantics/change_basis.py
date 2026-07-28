from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, cast

from belgi.profile.exceptions import ProfileError
from belgi.profile.reference_profile.declarations import ChangeBasisDeclaration
from belgi.profile.reference_profile.evidence.semantics import (
    unwrap_profile_declaration,
)
from belgi.profile.reference_profile.evidence.subject_access import (
    subject_field,
    subject_identity_present,
    subject_mapping_view,
)

if TYPE_CHECKING:
    from belgi.core import EvidenceState, JudgedObject


__all__ = [
    "change_basis_sat",
    "satisfies_change_basis",
]


def _component_mapping(component: object) -> Mapping[str, object] | None:
    return subject_mapping_view(subject_field(component, "value"))


def _has_identifier(component: object) -> bool:
    mapping = _component_mapping(component)
    if mapping is None:
        return False
    return subject_identity_present(
        mapping,
        "identifier",
        "proposal_identifier",
        "baseline_identifier",
        "revision_identifier",
        "source_state_identifier",
        "designator",
        "digest",
    )


def _has_resolved_source_state(component: object) -> bool:
    mapping = _component_mapping(component)
    if mapping is None:
        return False
    return subject_identity_present(
        mapping,
        "source_state",
        "source_state_identifier",
        "resolved_source_state",
        "tree_identifier",
        "snapshot_digest",
    )


def satisfies_change_basis(
    *,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
    condition: object,
) -> bool:
    del evidence_state
    declaration = unwrap_profile_declaration(condition, ChangeBasisDeclaration)
    admission_subject = subject_field(judged_object, "admission_subject")
    reference_context = subject_field(judged_object, "reference_context")
    if admission_subject is None or reference_context is None:
        return False
    if declaration.require_proposal_identifier and not _has_identifier(
        admission_subject
    ):
        return False
    if declaration.require_baseline_identifier and not _has_identifier(
        reference_context
    ):
        return False
    if declaration.require_proposal_source_state and not _has_resolved_source_state(
        admission_subject
    ):
        return False
    if declaration.require_baseline_source_state and not _has_resolved_source_state(
        reference_context
    ):
        return False
    return True


def change_basis_sat(
    judged_object: object,
    evidence_state: object,
    condition: object,
) -> bool:
    try:
        return satisfies_change_basis(
            judged_object=cast("JudgedObject", judged_object),
            evidence_state=cast("EvidenceState", evidence_state),
            condition=condition,
        )
    except (AttributeError, ProfileError, ValueError):
        return False
