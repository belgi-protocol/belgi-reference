"""Public rooted-snapshot API and platform dispatch."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from belgi.substrate.io.rooted import FilesystemIdentity

from .tree.model import (
    RootedTreeDirectoryDescendantPredicate,
    RootedTreeEntryValidator,
    RootedTreeLimits,
    RootedTreeSnapshot,
)


@dataclass(frozen=True, slots=True)
class RootedDirectorySnapshot:
    identity: FilesystemIdentity
    supports_state_writes: bool


@dataclass(frozen=True, slots=True)
class RootedPathAbsenceSnapshot:
    existing_parent_path: Path
    existing_parent_supports_state_writes: bool


@contextmanager
def open_binary_file_snapshot(
    path: Path,
    *,
    root: Path,
) -> Iterator[tuple[BinaryIO, FilesystemIdentity]]:
    if os.name == "nt":
        from .windows.file import open_windows_binary_file_snapshot

        owner = open_windows_binary_file_snapshot
    else:
        from .posix.file import open_posix_binary_file_snapshot

        owner = open_posix_binary_file_snapshot
    with owner(path, root=root) as snapshot:
        yield snapshot


@contextmanager
def open_directory_snapshot(
    path: Path,
    *,
    root: Path,
) -> Iterator[RootedDirectorySnapshot]:
    if os.name == "nt":
        from .windows.directory import open_windows_directory_snapshot

        owner = open_windows_directory_snapshot
    else:
        from .posix.directory import open_posix_directory_snapshot

        owner = open_posix_directory_snapshot
    with owner(path, root=root) as (identity, supports_state_writes):
        yield RootedDirectorySnapshot(
            identity=identity,
            supports_state_writes=supports_state_writes,
        )


@contextmanager
def open_path_absence_snapshot(
    path: Path,
    *,
    root: Path,
) -> Iterator[RootedPathAbsenceSnapshot]:
    if os.name == "nt":
        from .windows.directory import open_windows_path_absence_snapshot

        owner = open_windows_path_absence_snapshot
    else:
        from .posix.directory import open_posix_path_absence_snapshot

        owner = open_posix_path_absence_snapshot
    with owner(path, root=root) as (
        existing_parent_path,
        existing_parent_supports_state_writes,
    ):
        yield RootedPathAbsenceSnapshot(
            existing_parent_path=existing_parent_path,
            existing_parent_supports_state_writes=(
                existing_parent_supports_state_writes
            ),
        )


def rooted_regular_file_supports_state_writes(
    path: Path,
    *,
    root: Path,
    expected_identity: FilesystemIdentity,
) -> bool:
    if os.name == "nt":
        from .windows.file import (
            windows_rooted_regular_file_supports_state_writes,
        )

        owner = windows_rooted_regular_file_supports_state_writes
    else:
        from .posix.file import posix_rooted_regular_file_supports_state_writes

        owner = posix_rooted_regular_file_supports_state_writes
    return owner(
        path,
        root=root,
        expected_identity=expected_identity,
    )


def read_rooted_tree_snapshot(
    root: Path,
    *,
    limits: RootedTreeLimits,
    entry_validator: RootedTreeEntryValidator | None = None,
    directory_descendant_predicate: (
        RootedTreeDirectoryDescendantPredicate | None
    ) = None,
) -> RootedTreeSnapshot:
    from .tree.read import read_tree_snapshot_with_backend

    if os.name == "nt":
        from .windows.tree import WindowsRootedTreeBackend

        backend = WindowsRootedTreeBackend()
    else:
        from .posix.tree import PosixRootedTreeBackend

        backend = PosixRootedTreeBackend()
    return read_tree_snapshot_with_backend(
        root,
        limits=limits,
        backend=backend,
        entry_validator=entry_validator,
        directory_descendant_predicate=directory_descendant_predicate,
    )


__all__ = [
    "RootedDirectorySnapshot",
    "RootedPathAbsenceSnapshot",
    "open_binary_file_snapshot",
    "open_directory_snapshot",
    "open_path_absence_snapshot",
    "read_rooted_tree_snapshot",
    "rooted_regular_file_supports_state_writes",
]
