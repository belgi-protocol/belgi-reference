"""POSIX directory and absence snapshots."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from belgi.substrate.io.access import lexical_absolute_path
from belgi.substrate.io.posix.authentication import require_same_directory
from belgi.substrate.io.posix.metadata import directory_fingerprint, filesystem_identity
from belgi.substrate.io.posix.path_open import (
    open_directory_component,
    open_root_directory,
    require_path_component_absent,
)
from belgi.substrate.io.rooted import FilesystemIdentity

from .binding import (
    require_anchored_open_support,
    snapshot_path_error,
    snapshot_relative_path,
)


@contextmanager
def open_posix_directory_snapshot(
    path: Path,
    *,
    root: Path,
) -> Iterator[tuple[FilesystemIdentity, bool]]:
    absolute_root = lexical_absolute_path(root)
    absolute_path = lexical_absolute_path(path)
    if absolute_path == absolute_root:
        root, relative_path = absolute_root, Path()
    else:
        root, relative_path = snapshot_relative_path(
            root=absolute_root,
            path=absolute_path,
        )
    require_anchored_open_support()
    directory_descriptors: list[int] = []
    try:
        root_descriptor, root_status = open_root_directory(
            root,
            on_failure=snapshot_path_error,
        )
        directory_descriptors.append(root_descriptor)
        directory_fingerprints = [directory_fingerprint(root_status)]
        target_descriptor = root_descriptor
        target_status = root_status
        for component in relative_path.parts:
            target_descriptor, target_status = open_directory_component(
                parent_descriptor=target_descriptor,
                component=component,
                path=path,
                on_failure=snapshot_path_error,
            )
            directory_descriptors.append(target_descriptor)
            directory_fingerprints.append(directory_fingerprint(target_status))
        supports_state_writes = _directory_supports_state_writes(target_descriptor)
        try:
            yield filesystem_identity(target_status), supports_state_writes
        finally:
            final_fingerprints = [directory_fingerprint(os.fstat(root_descriptor))]
            final_descriptors: list[int] = []
            final_descriptor = root_descriptor
            try:
                for component in relative_path.parts:
                    final_descriptor, final_status = open_directory_component(
                        parent_descriptor=final_descriptor,
                        component=component,
                        path=path,
                        on_failure=snapshot_path_error,
                    )
                    final_descriptors.append(final_descriptor)
                    final_fingerprints.append(directory_fingerprint(final_status))
                final_supports = _directory_supports_state_writes(final_descriptor)
            finally:
                for descriptor in reversed(final_descriptors):
                    os.close(descriptor)
            require_same_directory(
                path=root,
                opened_status=root_status,
                path_status=root.lstat(),
                on_failure=snapshot_path_error,
            )
            if tuple(final_fingerprints) != tuple(directory_fingerprints):
                raise ValueError(f"directory path changed while loading: {path}")
            if final_supports != supports_state_writes:
                raise ValueError(f"directory access changed while loading: {path}")
    finally:
        for descriptor in reversed(directory_descriptors):
            os.close(descriptor)


@contextmanager
def open_posix_path_absence_snapshot(
    path: Path,
    *,
    root: Path,
) -> Iterator[tuple[Path, bool]]:
    root, relative_path = snapshot_relative_path(root=root, path=path)
    require_anchored_open_support()
    directory_descriptors: list[int] = []
    try:
        root_descriptor, root_status = open_root_directory(
            root,
            on_failure=snapshot_path_error,
        )
        directory_descriptors.append(root_descriptor)
        directory_fingerprints = [directory_fingerprint(root_status)]
        parent_descriptor = root_descriptor
        existing_parent_path = root
        absent_component = relative_path.parts[-1]
        for component in relative_path.parts[:-1]:
            try:
                parent_descriptor, parent_status = open_directory_component(
                    parent_descriptor=parent_descriptor,
                    component=component,
                    path=path,
                    on_failure=snapshot_path_error,
                )
            except FileNotFoundError:
                absent_component = component
                break
            directory_descriptors.append(parent_descriptor)
            directory_fingerprints.append(directory_fingerprint(parent_status))
            existing_parent_path /= component
        else:
            require_path_component_absent(
                parent_descriptor=parent_descriptor,
                component=absent_component,
                path=path,
                on_failure=snapshot_path_error,
            )
        supports_state_writes = _directory_supports_state_writes(parent_descriptor)
        try:
            yield existing_parent_path, supports_state_writes
        finally:
            final_fingerprints = [directory_fingerprint(os.fstat(root_descriptor))]
            final_descriptors: list[int] = []
            final_descriptor = root_descriptor
            try:
                parent_count = len(directory_fingerprints) - 1
                for component in relative_path.parts[:parent_count]:
                    final_descriptor, final_status = open_directory_component(
                        parent_descriptor=final_descriptor,
                        component=component,
                        path=path,
                        on_failure=snapshot_path_error,
                    )
                    final_descriptors.append(final_descriptor)
                    final_fingerprints.append(directory_fingerprint(final_status))
                require_path_component_absent(
                    parent_descriptor=final_descriptor,
                    component=absent_component,
                    path=path,
                    on_failure=snapshot_path_error,
                )
                final_supports = _directory_supports_state_writes(final_descriptor)
            finally:
                for descriptor in reversed(final_descriptors):
                    os.close(descriptor)
            require_same_directory(
                path=root,
                opened_status=root_status,
                path_status=root.lstat(),
                on_failure=snapshot_path_error,
            )
            if tuple(final_fingerprints) != tuple(directory_fingerprints):
                raise ValueError(f"path parent changed while loading: {path}")
            if final_supports != supports_state_writes:
                raise ValueError(f"path parent access changed while loading: {path}")
    finally:
        for descriptor in reversed(directory_descriptors):
            os.close(descriptor)


def _directory_supports_state_writes(descriptor: int) -> bool:
    try:
        return os.access(
            ".",
            os.W_OK | os.X_OK,
            dir_fd=descriptor,
            effective_ids=True,
            follow_symlinks=False,
        )
    except (NotImplementedError, OSError, TypeError):
        return False


__all__ = [
    "open_posix_directory_snapshot",
    "open_posix_path_absence_snapshot",
]
