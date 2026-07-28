from __future__ import annotations

from collections.abc import Mapping

from belgi.carrier import (
    CanonicalReference,
    ClaimRecord,
    DependencyKind,
    JudgedObjectCarrier,
    MemberClassification,
    MemberInventoryEntry,
    MemberRole,
)
from belgi.replay.carriers.content import resolved_content_locator_json_object
from belgi.replay.lifting.exceptions import ResolveFailureError
from belgi.replay.lifting.model import ResolvedDependencies, ResolvedPackageMember

__all__ = [
    "generic_source_state_dependency_references",
    "recover_generic_source_state_inputs",
    "require_generic_source_state_records",
    "require_generic_source_state_recovery",
]

_GENERIC_SOURCE_STATE_FIELDS = frozenset({"identifier", "source_state"})


def generic_source_state_dependency_references(
    *, claim_record: ClaimRecord, root_member: MemberInventoryEntry
) -> tuple[CanonicalReference, ...]:
    root_reference = root_member.canonical_reference
    if root_reference is None:
        return ()
    return tuple(
        declaration.dependency_reference
        for declaration in claim_record.dependency_declarations
        if declaration.dependent_reference == root_reference
        and declaration.dependency_kind is DependencyKind.JUDGED_OBJECT_INPUT
    )


def require_generic_source_state_recovery(
    *,
    carrier: JudgedObjectCarrier,
    dependencies: ResolvedDependencies,
    claim_record: ClaimRecord,
    root_member: MemberInventoryEntry,
) -> None:
    recover_generic_source_state_inputs(
        dependencies=dependencies,
        claim_record=claim_record,
        root_member=root_member,
    )
    proposal = resolved_content_locator_json_object(
        locator=carrier.proposal,
        dependencies=dependencies,
        claim_record=claim_record,
        description="judged-object carrier.proposal",
    )
    baseline = resolved_content_locator_json_object(
        locator=carrier.baseline,
        dependencies=dependencies,
        claim_record=claim_record,
        description="judged-object carrier.baseline",
    )
    require_generic_source_state_records(
        proposal=proposal,
        baseline=baseline,
        root_reference=root_member.canonical_reference,
    )


def recover_generic_source_state_inputs(
    *,
    dependencies: ResolvedDependencies,
    claim_record: ClaimRecord,
    root_member: MemberInventoryEntry,
) -> tuple[ResolvedPackageMember, ...]:
    root_reference = root_member.canonical_reference
    if root_reference is None:
        raise ResolveFailureError(
            message="Generic judged-object root lacks a canonical reference."
        )
    references = generic_source_state_dependency_references(
        claim_record=claim_record,
        root_member=root_member,
    )
    if not references:
        raise _source_state_failure(
            message=(
                "Part 4 ownership recovery requires at least one authenticated "
                "judged-object input."
            ),
            related_reference=root_reference,
        )
    if len(references) != len(set(references)):
        raise _source_state_failure(
            message="Part 4 ownership recovery has a duplicate judged-object input.",
            related_reference=root_reference,
        )
    return tuple(
        _require_recovered_judged_input(
            reference=reference,
            root_reference=root_reference,
            dependencies=dependencies,
            claim_record=claim_record,
        )
        for reference in references
    )


def require_generic_source_state_records(
    *,
    proposal: Mapping[str, object],
    baseline: Mapping[str, object],
    root_reference: CanonicalReference | None,
) -> None:
    if root_reference is None:
        raise ResolveFailureError(
            message="Generic judged-object root lacks a canonical reference."
        )
    for label, record in (("ProposalRecord", proposal), ("BaselineRecord", baseline)):
        if set(record) != _GENERIC_SOURCE_STATE_FIELDS:
            raise _source_state_failure(
                message=f"{label} must contain exactly its closed generic fields.",
                related_reference=root_reference,
            )
        for field in sorted(_GENERIC_SOURCE_STATE_FIELDS):
            value = record.get(field)
            if not isinstance(value, str) or not value:
                raise _source_state_failure(
                    message=f"{label}.{field} must be a non-empty exact string.",
                    related_reference=root_reference,
                )


def _require_recovered_judged_input(
    *,
    reference: CanonicalReference,
    root_reference: CanonicalReference,
    dependencies: ResolvedDependencies,
    claim_record: ClaimRecord,
) -> ResolvedPackageMember:
    declarations = tuple(
        declaration
        for declaration in claim_record.dependency_declarations
        if declaration.dependent_reference == root_reference
        and declaration.dependency_reference == reference
    )
    if (
        len(declarations) != 1
        or declarations[0].dependency_kind is not DependencyKind.JUDGED_OBJECT_INPUT
    ):
        raise _source_state_failure(
            message=(
                "Part 4 ownership input requires exactly one judged-object-input "
                "dependency from the judged root."
            ),
            related_reference=reference,
        )
    dependency = dependencies.member_for_reference(canonical_reference=reference)
    if dependency is None:
        raise _source_state_failure(
            message="Part 4 ownership input was not resolved.",
            related_reference=reference,
        )
    entry = dependency.inventory_entry
    if (
        entry.member_role is not MemberRole.REPLAY_DEPENDENCY
        or entry.classification is not MemberClassification.REPLAY_RELEVANT
        or not dependency.preserved_bytes
    ):
        raise _source_state_failure(
            message=(
                "Part 4 ownership input must be a non-empty replay-relevant "
                "replay-dependency."
            ),
            related_reference=reference,
        )
    return dependency


def _source_state_failure(
    *, message: str, related_reference: CanonicalReference
) -> ResolveFailureError:
    return ResolveFailureError(
        message=message,
        related_reference=related_reference,
    )
