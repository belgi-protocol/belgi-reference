"""Canonical-reference assignment for replay-relevant package members."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from .exceptions import (
    CanonicalReferenceError,
    DuplicateCanonicalReferenceError,
)
from .inventory import CanonicalReference, MemberName, PackageIdentifier

__all__ = [
    "CanonicalReferenceMap",
    "CanonicalReferencePolicy",
    "assign_canonical_references",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class CanonicalReferencePolicy:
    """Deterministic policy for package-local canonical-reference strings."""

    scheme: str = "pkg"

    def __post_init__(self) -> None:
        if self.scheme.strip() == "":
            raise CanonicalReferenceError(
                "Canonical-reference scheme must be non-empty."
            )


@dataclass(frozen=True, slots=True, kw_only=True)
class CanonicalReferenceMap:
    """Package-local mapping from member names to canonical references."""

    assignments: tuple[tuple[MemberName, CanonicalReference], ...]

    def __post_init__(self) -> None:
        seen_names: set[MemberName] = set()
        seen_references: set[CanonicalReference] = set()
        for member_name, canonical_reference in self.assignments:
            if member_name in seen_names:
                raise CanonicalReferenceError(
                    f"Duplicate member name in canonical-reference map: {member_name}"
                )
            if canonical_reference in seen_references:
                raise DuplicateCanonicalReferenceError(
                    f"Duplicate canonical reference: {canonical_reference}"
                )
            seen_names.add(member_name)
            seen_references.add(canonical_reference)

    def reference_for(self, member_name: MemberName) -> CanonicalReference:
        for assigned_name, assigned_reference in self.assignments:
            if assigned_name == member_name:
                return assigned_reference
        raise CanonicalReferenceError(f"Unknown member name: {member_name}")

    def as_dict(self) -> dict[MemberName, CanonicalReference]:
        return dict(self.assignments)


def assign_canonical_references(
    *,
    package_identifier: PackageIdentifier,
    replay_relevant_member_names: tuple[MemberName, ...],
    policy: CanonicalReferencePolicy | None = None,
) -> CanonicalReferenceMap:
    """Assign deterministic canonical references to replay-relevant member names."""

    active_policy = policy or CanonicalReferencePolicy()
    assignments: list[tuple[MemberName, CanonicalReference]] = []
    seen_names: set[MemberName] = set()
    seen_references: set[CanonicalReference] = set()
    for member_name in replay_relevant_member_names:
        if member_name in seen_names:
            raise CanonicalReferenceError(
                f"Duplicate replay-relevant member name: {member_name}"
            )
        seen_names.add(member_name)
        assigned_reference = CanonicalReference(
            f"{active_policy.scheme}:"
            f"{quote(str(package_identifier), safe='')}"
            f"#{quote(str(member_name), safe='')}"
        )
        if assigned_reference in seen_references:
            raise DuplicateCanonicalReferenceError(
                f"Duplicate canonical reference: {assigned_reference}"
            )
        assignments.append((member_name, assigned_reference))
        seen_references.add(assigned_reference)
    return CanonicalReferenceMap(assignments=tuple(assignments))
