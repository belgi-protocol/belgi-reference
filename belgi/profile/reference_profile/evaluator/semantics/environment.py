from __future__ import annotations

from typing import TYPE_CHECKING, cast

from belgi.profile.exceptions import ProfileError
from belgi.profile.reference_profile.declarations import (
    EnvironmentCompatibilityDeclaration,
    EnvironmentRequirement,
)
from belgi.profile.reference_profile.evidence.semantics import (
    bound_evidence_items,
    unwrap_profile_declaration,
)
from belgi.profile.reference_profile.evidence.subject_access import subject_field

if TYPE_CHECKING:
    from belgi.core import EvidenceState, JudgedObject


__all__ = [
    "environment_compatibility_sat",
    "satisfies_environment_compatibility",
]


def _environment_value(
    *, item: object, requirement: EnvironmentRequirement
) -> str | None:
    term_map = subject_field(item, "environment_terms", "environment")
    if isinstance(term_map, dict):
        value = term_map.get(str(requirement.term_id))
        if value is None:
            value = term_map.get(requirement.term_id)
        if value is not None:
            return str(value)
    candidate = subject_field(
        item,
        str(requirement.term_id),
        str(requirement.term_id).split(".")[-1].replace("-", "_"),
    )
    return str(candidate) if candidate is not None else None


def _has_equivalence_basis(
    *, item: object, declaration: EnvironmentCompatibilityDeclaration
) -> bool:
    if not declaration.equivalence_basis_identifiers:
        return False
    for field_name in ("equivalence_basis", "equivalence", "environment_equivalence"):
        value = subject_field(item, field_name)
        if value is None:
            continue
        if str(value) in declaration.equivalence_basis_identifiers:
            return True
    return False


def satisfies_environment_compatibility(
    *,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
    condition: object,
) -> bool:
    del judged_object
    declaration = unwrap_profile_declaration(
        condition,
        EnvironmentCompatibilityDeclaration,
    )
    for binding in declaration.required_bindings:
        items = bound_evidence_items(
            evidence_state=evidence_state,
            binding=binding,
            condition=declaration,
        )
        if len(items) < binding.minimum_count:
            return False
        for item in items:
            for requirement in declaration.required_terms:
                observed = _environment_value(item=item, requirement=requirement)
                if observed is None:
                    return False
                accepted = set(requirement.accepted_values)
                accepted.update(
                    str(identifier)
                    for identifier in declaration.accepted_toolchain_sets
                )
                if observed not in accepted and not _has_equivalence_basis(
                    item=item,
                    declaration=declaration,
                ):
                    return False
    return True


def environment_compatibility_sat(
    judged_object: object,
    evidence_state: object,
    condition: object,
) -> bool:
    try:
        return satisfies_environment_compatibility(
            judged_object=cast("JudgedObject", judged_object),
            evidence_state=cast("EvidenceState", evidence_state),
            condition=condition,
        )
    except (AttributeError, ProfileError, ValueError):
        return False
