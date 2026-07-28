from __future__ import annotations

from belgi.carrier import (
    CanonicalReference,
    ClaimRecord,
    DependencyKind,
    JudgedObjectCarrier,
    MemberClassification,
    MemberInventoryEntry,
    MemberRole,
)
from belgi.profile.reference_profile.finite_evaluator import (
    FiniteJudgedLiftError,
    finite_judged_source_state_identifiers,
)
from belgi.replay.lifting.exceptions import InduceFailureError, ResolveFailureError
from belgi.replay.lifting.model import ResolvedDependencies
from belgi.replay.parsing import require_inline_json_object

__all__ = [
    "finite_source_state_dependency_references",
    "require_finite_source_state_recovery",
]


def finite_source_state_dependency_references(
    *, carrier: JudgedObjectCarrier
) -> tuple[CanonicalReference, ...]:
    """Return finite recovery keys, deferring malformed records to lambda-J."""

    try:
        identifiers = finite_judged_source_state_identifiers(
            proposal=require_inline_json_object(
                locator=carrier.proposal,
                description="judged-object carrier.proposal",
            ),
            baseline=require_inline_json_object(
                locator=carrier.baseline,
                description="judged-object carrier.baseline",
            ),
        )
    except (FiniteJudgedLiftError, InduceFailureError):
        return ()
    return tuple(dict.fromkeys(CanonicalReference(value) for value in identifiers))


def require_finite_source_state_recovery(
    *,
    carrier: JudgedObjectCarrier,
    dependencies: ResolvedDependencies,
    claim_record: ClaimRecord,
    root_member: MemberInventoryEntry,
) -> None:
    """Require authenticated judged-input members before finite induction."""

    root_reference = root_member.canonical_reference
    if root_reference is None:
        raise ResolveFailureError(
            message="Finite judged-object root lacks a canonical reference."
        )
    for reference in finite_source_state_dependency_references(carrier=carrier):
        dependency = dependencies.member_for_reference(
            canonical_reference=reference,
        )
        if dependency is None:
            raise _unresolved_source_state(reference=reference)
        entry = dependency.inventory_entry
        if (
            entry.member_role is not MemberRole.REPLAY_DEPENDENCY
            or entry.classification is not MemberClassification.REPLAY_RELEVANT
            or not dependency.preserved_bytes
            or not _has_judged_input_declaration(
                claim_record=claim_record,
                root_reference=root_reference,
                dependency_reference=reference,
            )
        ):
            raise _unresolved_source_state(reference=reference)


def _has_judged_input_declaration(
    *,
    claim_record: ClaimRecord,
    root_reference: CanonicalReference,
    dependency_reference: CanonicalReference,
) -> bool:
    return any(
        declaration.dependent_reference == root_reference
        and declaration.dependency_reference == dependency_reference
        and declaration.dependency_kind is DependencyKind.JUDGED_OBJECT_INPUT
        for declaration in claim_record.dependency_declarations
    )


def _unresolved_source_state(*, reference: CanonicalReference) -> ResolveFailureError:
    return ResolveFailureError(
        message=(
            "Finite source-state recovery requires a non-empty authenticated "
            "replay-dependency declared as judged-object-input."
        ),
        related_reference=reference,
    )
