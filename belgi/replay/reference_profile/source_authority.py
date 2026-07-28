from __future__ import annotations

from enum import Enum

import belgi.profile.reference_profile.finite_evaluator as finite_evaluator
from belgi.carrier import (
    ClaimRecord,
    DependencyKind,
    Digest,
    ImmutableDesignator,
    MemberInventoryEntry,
    ReferencedSourceKind,
)
from belgi.replay.lifting.exceptions import ResolveFailureError
from belgi.replay.lifting.model import ResolvedDependencies, ResolvedReferencedSource

__all__ = [
    "Part4RootAuthority",
    "carrier_designator",
    "exact_part4_carrier_designator",
    "part4_root_authority",
    "require_resolved_source_authority",
    "resolved_source_designators",
    "root_references_part4_source",
]


class Part4RootAuthority(str, Enum):
    ABSENT = "absent"
    OWNERSHIP = "ownership"
    DETERMINING_SEMANTICS = "determining-semantics"


def carrier_designator(*, designator: object) -> ImmutableDesignator:
    uri = getattr(designator, "uri", None)
    digest = getattr(designator, "digest", None)
    algorithm_id = getattr(digest, "algorithm_id", None)
    digest_value = getattr(digest, "digest_value", None)
    if (
        not isinstance(uri, str)
        or not uri
        or not isinstance(algorithm_id, str)
        or not algorithm_id
        or not isinstance(digest_value, str)
        or not digest_value
    ):
        raise ValueError("exact owner designator is incomplete.")
    return ImmutableDesignator(
        uri=uri,
        digest=Digest(
            algorithm_id=algorithm_id,
            digest_value=digest_value,
        ),
    )


def exact_part4_carrier_designator() -> ImmutableDesignator:
    return carrier_designator(designator=finite_evaluator.PART4_DESIGNATOR)


def root_references_part4_source(
    *, claim_record: ClaimRecord, root_member: MemberInventoryEntry
) -> bool:
    designator = exact_part4_carrier_designator()
    root_reference = root_member.canonical_reference
    if root_reference is None:
        return False
    bindings = tuple(
        binding
        for binding in claim_record.referenced_sources
        if binding.designator == designator
    )
    if len(bindings) != 1:
        return False
    return any(
        dependency.dependent_reference == root_reference
        and dependency.dependency_reference == bindings[0].member_reference
        for dependency in claim_record.dependency_declarations
    )


def part4_root_authority(
    *, claim_record: ClaimRecord, root_member: MemberInventoryEntry
) -> Part4RootAuthority:
    designator = exact_part4_carrier_designator()
    root_reference = root_member.canonical_reference
    if root_reference is None:
        raise ResolveFailureError(
            message="Reference-profile root member lacks a canonical reference."
        )
    bindings = tuple(
        binding
        for binding in claim_record.referenced_sources
        if binding.designator == designator
    )
    if not bindings:
        return Part4RootAuthority.ABSENT
    if len(bindings) != 1:
        raise ResolveFailureError(
            message="Part 4 exact source binding is ambiguous.",
            related_reference=root_reference,
        )
    binding = bindings[0]
    dependency_kinds = frozenset(
        dependency.dependency_kind
        for dependency in claim_record.dependency_declarations
        if dependency.dependent_reference == root_reference
        and dependency.dependency_reference == binding.member_reference
    )
    if not dependency_kinds:
        return Part4RootAuthority.ABSENT
    if (
        binding.source_kind is ReferencedSourceKind.DETERMINING_SEMANTICS
        and DependencyKind.DETERMINING_SEMANTICS in dependency_kinds
    ):
        return Part4RootAuthority.DETERMINING_SEMANTICS
    if (
        binding.source_kind is ReferencedSourceKind.PROFILE
        and DependencyKind.PROFILE_MATERIAL in dependency_kinds
        and DependencyKind.DETERMINING_SEMANTICS not in dependency_kinds
    ):
        return Part4RootAuthority.OWNERSHIP
    observed = ", ".join(sorted(kind.value for kind in dependency_kinds))
    raise ResolveFailureError(
        message=(
            "Part 4 source/dependency authority mismatch for root member "
            f"{root_reference!r}: sourceKind={binding.source_kind.value!r}, "
            f"dependencyKinds={observed!r}."
        ),
        related_reference=binding.member_reference,
    )


def require_resolved_source_authority(
    *,
    resolved: ResolvedDependencies,
    claim_record: ClaimRecord,
    root_member: MemberInventoryEntry,
    designator: ImmutableDesignator,
    allowed_roles: tuple[tuple[ReferencedSourceKind, DependencyKind], ...],
) -> ResolvedReferencedSource:
    root_reference = root_member.canonical_reference
    if root_reference is None:
        raise ResolveFailureError(
            message="Reference-profile root member lacks a canonical reference."
        )
    source = next(
        (
            candidate
            for candidate in resolved.referenced_sources
            if candidate.binding.designator == designator
        ),
        None,
    )
    if source is None:
        raise ResolveFailureError(
            message=f"Exact evidence source {designator!s} was not resolved.",
            related_reference=root_reference,
        )
    matching_roles = tuple(
        dependency_kind
        for source_kind, dependency_kind in allowed_roles
        if source.binding.source_kind is source_kind
    )
    if len(matching_roles) != 1:
        expected = ", ".join(
            f"{source_kind.value}/{dependency_kind.value}"
            for source_kind, dependency_kind in allowed_roles
        )
        raise ResolveFailureError(
            message=(
                f"Exact source {designator!s} has source kind "
                f"{source.binding.source_kind.value!r}; expected one of {expected}."
            ),
            related_reference=source.binding.member_reference,
        )
    declarations = tuple(
        dependency
        for dependency in claim_record.dependency_declarations
        if dependency.dependent_reference == root_reference
        and dependency.dependency_reference == source.binding.member_reference
    )
    expected_kind = matching_roles[0]
    if (
        sum(
            declaration.dependency_kind is expected_kind for declaration in declarations
        )
        != 1
    ):
        raise ResolveFailureError(
            message=(
                f"Exact source {designator!s} requires one "
                f"{expected_kind.value!r} dependency from root member "
                f"{root_reference!r}."
            ),
            related_reference=source.binding.member_reference,
        )
    return source


def resolved_source_designators(
    *, resolved: ResolvedDependencies
) -> tuple[ImmutableDesignator, ...]:
    return tuple(
        source.verified_source.immutable_designator
        for source in resolved.referenced_sources
    )
