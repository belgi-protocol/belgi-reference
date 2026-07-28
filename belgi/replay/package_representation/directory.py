"""Directory projection from stable physical snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from belgi.carrier.package.representation.binding import (
    PackageRepresentationBinding,
    require_selected_binding,
)
from belgi.carrier.package.representation.contract import (
    BASELINE_ENVELOPE,
    PackageResourceEnvelope,
)
from belgi.carrier.package.representation.paths import (
    logical_path_for_physical_path,
    require_complete_entry_set,
    require_portable_logical_path,
)
from belgi.substrate.io.rooted_snapshot.api import read_rooted_tree_snapshot
from belgi.substrate.io.rooted_snapshot.tree.exceptions import RootedTreeError
from belgi.substrate.io.rooted_snapshot.tree.model import (
    RootedTreeFailureKind,
    RootedTreeLimits,
    RootedTreeNodeFact,
    RootedTreeNodeKind,
)

from .exceptions import DirectoryEntrySetError
from .model import LogicalMember, RepresentationResult, accepted_result, rejected_result

__all__ = [
    "DirectoryEntrySnapshot",
    "DirectoryProjectionSnapshot",
    "project_directory_path",
    "project_directory_snapshot",
]

_TREE_ERROR_RESULTS = {
    RootedTreeFailureKind.INVALID_ENTRY_NAME: (4, "invalid-entry-name"),
    RootedTreeFailureKind.UNSUPPORTED_ENTRY_TYPE: (4, "unsupported-entry-type"),
    RootedTreeFailureKind.DIRECTORY_ENTRY_COUNT: (3, "entry-count-exceeded"),
    RootedTreeFailureKind.MEMBER_COUNT: (3, "entry-count-exceeded"),
    RootedTreeFailureKind.MEMBER_SIZE: (5, "member-size-exceeded"),
    RootedTreeFailureKind.TOTAL_SIZE: (5, "total-size-exceeded"),
}


@dataclass(frozen=True, slots=True, kw_only=True)
class DirectoryEntrySnapshot:
    physical_path: str
    node_type: str
    octets: bytes | None = None
    link_count: int | None = None
    identity_stable: bool = True
    type_stable: bool = True
    size_stable: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class DirectoryProjectionSnapshot:
    root_node_type: str
    root_identity_stable: bool
    ancestors_stable: bool
    entries: tuple[DirectoryEntrySnapshot, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class _EntryObservation:
    physical_path: str
    node_type: str
    link_count: int | None
    structural_directory: bool = False


def project_directory_path(
    root: Path,
    *,
    selected_binding: PackageRepresentationBinding,
    supported_binding: PackageRepresentationBinding,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> RepresentationResult:
    require_selected_binding(selected=selected_binding, supported=supported_binding)
    try:
        snapshot = read_rooted_tree_snapshot(
            root,
            limits=RootedTreeLimits(
                directory_entry_count=envelope.directory_entry_count,
                member_count=envelope.member_count,
                member_bytes=envelope.member_bytes,
                total_member_bytes=envelope.total_member_bytes,
                path_segments=envelope.path_segments,
                path_segment_bytes=envelope.path_segment_bytes,
                path_bytes=envelope.path_bytes,
            ),
            entry_validator=lambda facts: _require_native_entry_set(
                facts,
                envelope=envelope,
            ),
            directory_descendant_predicate=lambda fact: _can_prefix_portable_member(
                fact.relative_path,
                envelope=envelope,
            ),
        )
    except DirectoryEntrySetError as exc:
        return rejected_result(stage=4, result_code=exc.result_code)
    except RootedTreeError as exc:
        stage, result_code = _TREE_ERROR_RESULTS.get(
            exc.kind,
            (5, "package-mutated-during-read"),
        )
        return rejected_result(stage=stage, result_code=result_code)
    return accepted_result(
        _logical_members(
            tuple((entry.relative_path, entry.octets) for entry in snapshot.entries),
            envelope=envelope,
        )
    )


def project_directory_snapshot(
    snapshot: DirectoryProjectionSnapshot,
    *,
    selected_binding: PackageRepresentationBinding,
    supported_binding: PackageRepresentationBinding,
    envelope: PackageResourceEnvelope = BASELINE_ENVELOPE,
) -> RepresentationResult:
    require_selected_binding(selected=selected_binding, supported=supported_binding)
    if len(snapshot.entries) > envelope.directory_entry_count:
        return rejected_result(stage=3, result_code="entry-count-exceeded")
    if (
        sum(entry.node_type != "directory" for entry in snapshot.entries)
        > envelope.member_count
    ):
        return rejected_result(stage=3, result_code="entry-count-exceeded")
    if snapshot.root_node_type != "directory":
        return rejected_result(stage=4, result_code="unsupported-entry-type")

    defect = _entry_set_defect(
        tuple(
            _EntryObservation(
                physical_path=entry.physical_path,
                node_type=entry.node_type,
                link_count=entry.link_count,
            )
            for entry in snapshot.entries
        ),
        envelope=envelope,
    )
    if defect is not None:
        return rejected_result(stage=4, result_code=defect)

    observed_octets = tuple(
        entry.octets for entry in snapshot.entries if entry.octets is not None
    )
    if any(len(octets) > envelope.member_bytes for octets in observed_octets):
        return rejected_result(stage=5, result_code="member-size-exceeded")
    if sum(len(octets) for octets in observed_octets) > envelope.total_member_bytes:
        return rejected_result(stage=5, result_code="total-size-exceeded")
    if len(observed_octets) != len(snapshot.entries):
        return rejected_result(stage=5, result_code="package-mutated-during-read")
    if (
        not snapshot.root_identity_stable
        or not snapshot.ancestors_stable
        or any(
            not entry.identity_stable or not entry.type_stable or not entry.size_stable
            for entry in snapshot.entries
        )
    ):
        return rejected_result(
            stage=5,
            result_code="package-mutated-during-read",
        )
    return accepted_result(
        _logical_members(
            tuple(
                (entry.physical_path, bytes(entry.octets))
                for entry in snapshot.entries
                if entry.octets is not None
            ),
            envelope=envelope,
        )
    )


def _logical_members(
    entries: tuple[tuple[str, bytes], ...],
    *,
    envelope: PackageResourceEnvelope,
) -> tuple[LogicalMember, ...]:
    return tuple(
        LogicalMember(
            logical_path=logical_path_for_physical_path(
                physical_path,
                envelope=envelope,
            ),
            octets=octets,
        )
        for physical_path, octets in entries
    )


def _can_prefix_portable_member(
    physical_directory_path: str,
    *,
    envelope: PackageResourceEnvelope,
) -> bool:
    try:
        require_portable_logical_path(
            physical_directory_path,
            envelope=envelope,
        )
    except ValueError:
        return False
    return (
        len(physical_directory_path.split("/")) < envelope.path_segments
        and len(physical_directory_path.encode("ascii")) + 2 <= envelope.path_bytes
    )


def _require_native_entry_set(
    facts: tuple[RootedTreeNodeFact, ...],
    *,
    envelope: PackageResourceEnvelope,
) -> None:
    paths_with_file_descendants: set[str] = set()
    for fact in facts:
        if fact.kind is not RootedTreeNodeKind.REGULAR_FILE:
            continue
        components = fact.relative_path.split("/")
        paths_with_file_descendants.update(
            "/".join(components[:component_count])
            for component_count in range(1, len(components))
        )
    defect = _entry_set_defect(
        tuple(
            _EntryObservation(
                physical_path=fact.relative_path,
                node_type=fact.kind.value,
                link_count=fact.link_count,
                structural_directory=(
                    fact.kind is RootedTreeNodeKind.DIRECTORY
                    and fact.relative_path in paths_with_file_descendants
                ),
            )
            for fact in facts
        ),
        envelope=envelope,
    )
    if defect is not None:
        raise DirectoryEntrySetError(defect)


def _entry_set_defect(
    entries: tuple[_EntryObservation, ...],
    *,
    envelope: PackageResourceEnvelope,
) -> str | None:
    invalid_name = False
    unsupported_type = False
    leaf_paths: list[str] = []
    all_paths: list[str] = []
    for entry in entries:
        all_paths.append(entry.physical_path)
        try:
            if entry.node_type == "directory" and entry.structural_directory:
                require_portable_logical_path(
                    entry.physical_path,
                    envelope=envelope,
                )
            else:
                logical_path_for_physical_path(
                    entry.physical_path,
                    envelope=envelope,
                )
        except ValueError:
            invalid_name = True
        if entry.node_type == "directory" and entry.structural_directory:
            continue
        leaf_paths.append(entry.physical_path)
        if entry.node_type != "regular-file" or entry.link_count != 1:
            unsupported_type = True
    if invalid_name:
        return "invalid-entry-name"
    if unsupported_type:
        return "unsupported-entry-type"
    if len(set(all_paths)) != len(all_paths):
        return "duplicate-entry"
    try:
        require_complete_entry_set(tuple(leaf_paths))
    except ValueError:
        return "path-prefix-collision"
    return None
