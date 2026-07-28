from __future__ import annotations

from collections.abc import Iterable

from belgi.core import EvidenceState, project_evidence_state
from belgi.profile.reference_profile.evidence.ownership import (
    EvidenceKindOwnershipRegistry,
)
from belgi.profile.reference_profile.exceptions import ReferenceProfileReplayError
from belgi.profile.reference_profile.finite_evaluator.constants import (
    PART4_DESIGNATOR,
    RECOGNIZED_EVIDENCE_KINDS,
)
from belgi.profile.reference_profile.finite_evaluator.evidence import (
    induce_finite_evidence_state_carrier_items,
)
from belgi.profile.reference_profile.finite_evaluator.exceptions import (
    FiniteEvidenceLiftError,
)
from belgi.profile.reference_profile.identifiers.evidence_kinds import REVIEW_RECORD

from .generic_induction import reference_profile_generic_evidence_item

__all__ = ["reference_profile_evidence_state_from_carrier_items"]


def reference_profile_evidence_state_from_carrier_items(
    *,
    carrier_items: Iterable[object],
    resolved_owner_designators: tuple[object, ...],
    ownership_registry: EvidenceKindOwnershipRegistry,
) -> EvidenceState:
    carrier_items = tuple(carrier_items)
    resolved_keys = frozenset(
        (
            getattr(designator, "uri", None),
            getattr(getattr(designator, "digest", None), "algorithm_id", None),
            getattr(getattr(designator, "digest", None), "digest_value", None),
        )
        for designator in resolved_owner_designators
    )
    for item in carrier_items:
        identifier = str(getattr(item, "evidence_kind_identifier", ""))
        owner = ownership_registry.require_owner(evidence_kind_identifier=identifier)
        if owner.immutable_designator.stable_key not in resolved_keys:
            raise ReferenceProfileReplayError(
                f"evidence kind owner exact source was not resolved for {identifier!r}."
            )
    part4_owner_resolved = PART4_DESIGNATOR.stable_key in resolved_keys
    return project_evidence_state(
        items=tuple(
            _evidence_item_with_owner(
                item=item,
                ordinal=ordinal,
                part4_owner_resolved=part4_owner_resolved,
            )
            for ordinal, item in enumerate(carrier_items, start=1)
        ),
    )


def _evidence_item_with_owner(
    *, item: object, ordinal: int, part4_owner_resolved: bool
) -> object:
    evidence_kind = str(getattr(item, "evidence_kind_identifier", ""))
    package_member_octets = getattr(item, "source_preserved_octets", None)
    if part4_owner_resolved and (
        evidence_kind == REVIEW_RECORD
        or (
            evidence_kind in RECOGNIZED_EVIDENCE_KINDS
            and package_member_octets is not None
        )
    ):
        try:
            state = induce_finite_evidence_state_carrier_items(carrier_items=(item,))
        except FiniteEvidenceLiftError as exc:
            raise ReferenceProfileReplayError(
                "Part 4 evidence carrier induction failed."
            ) from exc
        if len(state.items) != 1:
            raise ReferenceProfileReplayError(
                "strict Part 4 review induction did not produce one evidence item."
            )
        return state.items[0]
    return reference_profile_generic_evidence_item(item=item, ordinal=ordinal)
