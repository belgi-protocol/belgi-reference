"""POSIX regular-file snapshot and write-access observation."""

from __future__ import annotations

import errno
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO

from belgi.substrate.io.posix.authentication import (
    require_same_directory,
    require_same_regular_file,
)
from belgi.substrate.io.posix.metadata import (
    directory_fingerprint,
    filesystem_identity,
    regular_file_fingerprint,
)
from belgi.substrate.io.posix.path_open import (
    open_directory_component,
    open_regular_file_component,
    open_root_directory,
    path_component_status,
    try_open_regular_file_component,
)
from belgi.substrate.io.rooted import FilesystemIdentity, PathFingerprint

from .binding import (
    require_anchored_open_support,
    snapshot_path_error,
    snapshot_relative_path,
)


@contextmanager
def open_posix_binary_file_snapshot(
    path: Path,
    *,
    root: Path,
) -> Iterator[tuple[BinaryIO, FilesystemIdentity]]:
    root, relative_path = snapshot_relative_path(root=root, path=path)
    require_anchored_open_support()
    directory_descriptors: list[int] = []
    descriptor = -1
    stream: BinaryIO | None = None
    try:
        root_descriptor, root_status = open_root_directory(
            root,
            on_failure=snapshot_path_error,
        )
        directory_descriptors.append(root_descriptor)
        directory_fingerprints = [directory_fingerprint(root_status)]
        parent_descriptor = root_descriptor
        for component in relative_path.parts[:-1]:
            parent_descriptor, parent_status = open_directory_component(
                parent_descriptor=parent_descriptor,
                component=component,
                path=path,
                on_failure=snapshot_path_error,
            )
            directory_descriptors.append(parent_descriptor)
            directory_fingerprints.append(directory_fingerprint(parent_status))
        descriptor, opened_status = open_regular_file_component(
            parent_descriptor=parent_descriptor,
            component=relative_path.parts[-1],
            path=path,
            on_failure=snapshot_path_error,
        )
        stream = os.fdopen(descriptor, "rb")
        descriptor = -1
        opened_fingerprint = regular_file_fingerprint(opened_status)
        identity = filesystem_identity(opened_status)
        try:
            yield stream, identity
        finally:
            final_opened_status = os.fstat(stream.fileno())
            final_directory_fingerprints, final_path_status = _rooted_path_status(
                root_descriptor=root_descriptor,
                relative_path=relative_path,
            )
            require_same_directory(
                path=root,
                opened_status=root_status,
                path_status=root.lstat(),
                on_failure=snapshot_path_error,
            )
            if final_directory_fingerprints != tuple(directory_fingerprints):
                raise ValueError(f"file parent path changed while loading: {path}")
            require_same_regular_file(
                path=path,
                opened_status=final_opened_status,
                path_status=final_path_status,
                on_failure=snapshot_path_error,
            )
            if regular_file_fingerprint(final_opened_status) != opened_fingerprint:
                raise ValueError(f"file changed while loading: {path}")
    finally:
        if stream is not None:
            stream.close()
        elif descriptor >= 0:
            os.close(descriptor)
        for directory_descriptor in reversed(directory_descriptors):
            os.close(directory_descriptor)


def posix_rooted_regular_file_supports_state_writes(
    path: Path,
    *,
    root: Path,
    expected_identity: FilesystemIdentity,
) -> bool:
    root, relative_path = snapshot_relative_path(root=root, path=path)
    require_anchored_open_support()
    directory_descriptors: list[int] = []
    write_descriptor = -1
    try:
        root_descriptor, _ = open_root_directory(
            root,
            on_failure=snapshot_path_error,
        )
        directory_descriptors.append(root_descriptor)
        parent_descriptor = root_descriptor
        for component in relative_path.parts[:-1]:
            parent_descriptor, _ = open_directory_component(
                parent_descriptor=parent_descriptor,
                component=component,
                path=path,
                on_failure=snapshot_path_error,
            )
            directory_descriptors.append(parent_descriptor)
        opened = try_open_regular_file_component(
            parent_descriptor=parent_descriptor,
            component=relative_path.parts[-1],
            path=path,
            writable=True,
            expected_identity=expected_identity,
            on_failure=snapshot_path_error,
            open_unavailable=_write_open_unavailable,
        )
        if opened is None:
            return False
        write_descriptor, _ = opened
        return True
    finally:
        if write_descriptor >= 0:
            os.close(write_descriptor)
        for directory_descriptor in reversed(directory_descriptors):
            os.close(directory_descriptor)


def _write_open_unavailable(error: OSError) -> bool:
    return isinstance(error, PermissionError) or error.errno == errno.EROFS


def _rooted_path_status(
    *,
    root_descriptor: int,
    relative_path: Path,
) -> tuple[tuple[PathFingerprint, ...], os.stat_result]:
    opened_directories: list[int] = []
    directory_fingerprints = [directory_fingerprint(os.fstat(root_descriptor))]
    parent_descriptor = root_descriptor
    try:
        for component in relative_path.parts[:-1]:
            parent_descriptor, parent_status = open_directory_component(
                parent_descriptor=parent_descriptor,
                component=component,
                path=relative_path,
                on_failure=snapshot_path_error,
            )
            opened_directories.append(parent_descriptor)
            directory_fingerprints.append(directory_fingerprint(parent_status))
        path_status = path_component_status(
            parent_descriptor=parent_descriptor,
            component=relative_path.parts[-1],
            path=relative_path,
            on_failure=snapshot_path_error,
        )
        return tuple(directory_fingerprints), path_status
    finally:
        for directory_descriptor in reversed(opened_directories):
            os.close(directory_descriptor)


__all__ = [
    "open_posix_binary_file_snapshot",
    "posix_rooted_regular_file_supports_state_writes",
]
