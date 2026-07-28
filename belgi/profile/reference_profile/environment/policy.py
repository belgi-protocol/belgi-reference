from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping

from belgi.profile.reference_profile.identifiers.conditions import (
    ENVIRONMENT_COMPATIBILITY_SATISFIED,
)

__all__ = [
    "evidence_uses_environment_envelope",
    "require_environment_compatibility_condition",
]


def evidence_uses_environment_envelope(*, evidence: object) -> bool:
    items = getattr(evidence, "items", ())
    if not isinstance(items, Iterable) or isinstance(items, (str, bytes)):
        return False
    for item in items:
        environment_terms = getattr(item, "environment_terms", None)
        if isinstance(environment_terms, Mapping) and environment_terms:
            return True
        if getattr(item, "equivalence_basis", None) is not None:
            return True
    return False


def require_environment_compatibility_condition(
    *,
    declared_condition_ids: Collection[object],
    environment_envelope_present: bool,
    surface_label: str,
) -> None:
    if not environment_envelope_present:
        return
    if {str(condition_id) for condition_id in declared_condition_ids}.issuperset(
        {str(ENVIRONMENT_COMPATIBILITY_SATISFIED)}
    ):
        return
    raise ValueError(
        f"{surface_label} requires declaration of "
        f"{ENVIRONMENT_COMPATIBILITY_SATISFIED!s}."
    )
