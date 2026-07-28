"""Held POSIX capability for one alias-free absolute root ancestry."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from belgi.substrate.io.access import lexical_absolute_path
from belgi.substrate.io.posix.metadata import directory_fingerprint
from belgi.substrate.io.posix.path_open import (
    open_directory_component,
    open_root_directory,
)
from belgi.substrate.io.rooted import PathFingerprint, RootedPathFailure
from belgi.substrate.io.rooted_snapshot.tree.exceptions import RootedTreeError
from belgi.substrate.io.rooted_snapshot.tree.model import RootedTreeFailureKind

from .binding import snapshot_path_error

__all__ = ["PosixRootedTreeAncestry", "open_posix_rooted_tree_ancestry"]


@dataclass(frozen=True, slots=True, kw_only=True)
class PosixRootedTreeAncestry:
    root: Path
    descriptors: tuple[int, ...]
    observations: tuple[PathFingerprint, ...]

    @property
    def root_descriptor(self) -> int:
        return self.descriptors[-1]

    def require_current(self) -> None:
        held = tuple(
            directory_fingerprint(os.fstat(descriptor))
            for descriptor in self.descriptors
        )
        if held != self.observations:
            raise ValueError(
                f"root ancestry changed during bounded reading: {self.root}"
            )
        try:
            _root, reopened, statuses = _open_posix_absolute_directory_chain(self.root)
        except (OSError, ValueError) as exc:
            raise ValueError(
                f"root ancestry changed during bounded reading: {self.root}"
            ) from exc
        try:
            reopened_observations = tuple(
                directory_fingerprint(status) for status in statuses
            )
            if reopened_observations != self.observations:
                raise ValueError(
                    f"root ancestry changed during bounded reading: {self.root}"
                )
        finally:
            for descriptor in reversed(reopened):
                os.close(descriptor)

    def close(self) -> None:
        for descriptor in reversed(self.descriptors):
            os.close(descriptor)


@contextmanager
def open_posix_rooted_tree_ancestry(
    root: Path,
) -> Iterator[PosixRootedTreeAncestry]:
    absolute_root, descriptors, statuses = _open_posix_absolute_directory_chain(root)
    try:
        ancestry = PosixRootedTreeAncestry(
            root=absolute_root,
            descriptors=tuple(descriptors),
            observations=tuple(directory_fingerprint(status) for status in statuses),
        )
        try:
            yield ancestry
        except BaseException:
            raise
        else:
            ancestry.require_current()
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _open_posix_absolute_directory_chain(
    path: Path,
) -> tuple[Path, list[int], tuple[os.stat_result, ...]]:
    absolute_path = lexical_absolute_path(path)
    if absolute_path.anchor != os.sep:
        raise RootedTreeError(
            RootedTreeFailureKind.UNSUPPORTED_ENTRY_TYPE,
            "POSIX rooted trees require one filesystem-root anchor",
        )
    descriptors: list[int] = []
    statuses: list[os.stat_result] = []
    try:
        anchor_descriptor, anchor_status = open_root_directory(
            Path(os.sep),
            on_failure=snapshot_path_error,
        )
        descriptors.append(anchor_descriptor)
        statuses.append(anchor_status)
        current_path = Path(os.sep)
        ancestry_path_error = partial(
            _absolute_ancestry_path_error,
            expected_root=absolute_path,
        )
        for component in absolute_path.parts[1:]:
            current_path /= component
            descriptor, status = open_directory_component(
                parent_descriptor=descriptors[-1],
                component=component,
                path=current_path,
                on_failure=ancestry_path_error,
            )
            descriptors.append(descriptor)
            statuses.append(status)
        return absolute_path, descriptors, tuple(statuses)
    except BaseException:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise


def _absolute_ancestry_path_error(
    failure: RootedPathFailure,
    path: Path,
    *,
    expected_root: Path,
) -> BaseException:
    if failure is RootedPathFailure.EXPECTED_DIRECTORY and path == expected_root:
        return RootedTreeError(
            RootedTreeFailureKind.UNSUPPORTED_ENTRY_TYPE,
            "root must be one real directory",
        )
    return snapshot_path_error(failure, path)
