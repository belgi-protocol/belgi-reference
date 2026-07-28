from __future__ import annotations

from belgi.carrier import (
    CanonicalReference,
    ClaimRecord,
    ImmutableDesignator,
    MemberInventoryEntry,
    ReferencedSourceBinding,
)
from belgi.replay.lifting.exceptions import (
    AmbientContextRequiredError,
    ResolveFailureError,
)
from belgi.replay.lifting.members import resolve_package_member
from belgi.replay.lifting.model import (
    ResolvedDependencies,
    ResolvedPackageMember,
    ResolvedReferencedSource,
)
from belgi.replay.lifting.source_binding import validate_referenced_source_bytes
from belgi.replay.package_source.protocol import ReplayPackageSource

__all__ = ["resolve_declared_dependencies"]


def resolve_declared_dependencies(
    *,
    claim_record: ClaimRecord,
    package: ReplayPackageSource,
    source_member: MemberInventoryEntry,
    dependency_references: tuple[CanonicalReference, ...],
    exact_edition_designators: tuple[ImmutableDesignator, ...],
) -> ResolvedDependencies:
    source_reference = source_member.canonical_reference
    if source_reference is None:
        raise ResolveFailureError(
            message="Root carrier members must carry canonical references."
        )
    declared_references = {
        dependency.dependency_reference
        for dependency in claim_record.dependency_declarations
        if dependency.dependent_reference == source_reference
    }
    resolved_members = tuple(
        _resolve_member_dependency(
            claim_record=claim_record,
            package=package,
            source_reference=source_reference,
            reference=reference,
            declared_references=declared_references,
        )
        for reference in dict.fromkeys(dependency_references)
    )
    resolved_sources = tuple(
        _resolve_referenced_source(
            claim_record=claim_record,
            package=package,
            source_reference=source_reference,
            designator=designator,
            declared_references=declared_references,
        )
        for designator in dict.fromkeys(exact_edition_designators)
    )
    return ResolvedDependencies(
        member_dependencies=resolved_members,
        referenced_sources=resolved_sources,
    )


def _resolve_member_dependency(
    *,
    claim_record: ClaimRecord,
    package: ReplayPackageSource,
    source_reference: CanonicalReference,
    reference: CanonicalReference,
    declared_references: set[CanonicalReference],
) -> ResolvedPackageMember:
    if reference not in declared_references:
        raise ResolveFailureError(
            message=(
                f"Parsed carrier requested undeclared dependency {reference!r} from "
                f"root member {source_reference!r}."
            ),
            related_reference=reference,
        )
    try:
        inventory_entry = claim_record.member_inventory.entry_for_reference(
            canonical_reference=reference
        )
    except Exception as exc:
        raise ResolveFailureError(
            message=(
                f"Declared dependency {reference!r} could not be resolved in "
                "the claim record."
            ),
            related_reference=reference,
        ) from exc
    if not package.has_member(inventory_entry=inventory_entry):
        raise ResolveFailureError(
            message=(
                f"Declared dependency {reference!r} is not present in the "
                "replay package."
            ),
            related_reference=reference,
        )
    return resolve_package_member(package=package, inventory_entry=inventory_entry)


def _resolve_referenced_source(
    *,
    claim_record: ClaimRecord,
    package: ReplayPackageSource,
    source_reference: CanonicalReference,
    designator: ImmutableDesignator,
    declared_references: set[CanonicalReference],
) -> ResolvedReferencedSource:
    binding = _referenced_source_for_designator(
        claim_record=claim_record,
        designator=designator,
    )
    if binding is None:
        raise AmbientContextRequiredError(
            message=(
                f"Parsed carrier requested exact-edition dependency {designator!s}, "
                "but no referenced-source binding was preserved."
            ),
            related_reference=source_reference,
        )
    if binding.member_reference not in declared_references:
        raise ResolveFailureError(
            message=(
                f"Referenced source {designator!s} is not declared as a package-local "
                f"dependency of root member {source_reference!r}."
            ),
            related_reference=source_reference,
        )
    try:
        inventory_entry = claim_record.member_inventory.entry_for_reference(
            canonical_reference=binding.member_reference
        )
    except Exception as exc:
        raise ResolveFailureError(
            message=(
                f"Referenced source member {binding.member_reference!r} could not "
                "be resolved in the claim record."
            ),
            related_reference=binding.member_reference,
        ) from exc
    if not package.has_member(inventory_entry=inventory_entry):
        raise AmbientContextRequiredError(
            message=(
                f"Referenced source member {binding.member_reference!r} is not "
                "preserved in the replay package."
            ),
            related_reference=binding.member_reference,
        )
    resolved_member = resolve_package_member(
        package=package,
        inventory_entry=inventory_entry,
    )
    try:
        verified_source = validate_referenced_source_bytes(
            preserved_bytes=resolved_member.preserved_bytes,
            binding=binding,
            description=f"referenced source {binding.member_reference!r}",
        )
    except ValueError as exc:
        raise ResolveFailureError(
            message=str(exc),
            related_reference=binding.member_reference,
        ) from exc
    return ResolvedReferencedSource(
        member=resolved_member,
        binding=binding,
        verified_source=verified_source,
    )


def _referenced_source_for_designator(
    *,
    claim_record: ClaimRecord,
    designator: ImmutableDesignator,
) -> ReferencedSourceBinding | None:
    return next(
        (
            binding
            for binding in claim_record.referenced_sources
            if binding.designator == designator
        ),
        None,
    )
