"""Regular-file reading relative to one held POSIX rooted-tree capability."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO

from belgi.substrate.io.posix.authentication import require_same_regular_file
from belgi.substrate.io.posix.metadata import (
    directory_fingerprint,
    filesystem_identity,
    regular_file_fingerprint,
)
from belgi.substrate.io.posix.path_open import (
    open_directory_component,
    open_regular_file_component,
    path_component_status,
)
from belgi.substrate.io.rooted import FilesystemIdentity

from .binding import snapshot_path_error

__all__ = ["open_posix_rooted_tree_file"]


@contextmanager
def open_posix_rooted_tree_file(
    *,
    root_descriptor: int,
    relative_path: tuple[str, ...],
) -> Iterator[tuple[BinaryIO, FilesystemIdentity]]:
    if not relative_path:
        raise ValueError("rooted tree file path must not be empty")
    display_path = Path(*relative_path)
    directory_descriptors: list[int] = []
    descriptor = -1
    stream: BinaryIO | None = None
    parent_descriptor = root_descriptor
    directory_observations = [directory_fingerprint(os.fstat(root_descriptor))]
    try:
        for component in relative_path[:-1]:
            parent_descriptor, parent_status = open_directory_component(
                parent_descriptor=parent_descriptor,
                component=component,
                path=display_path,
                on_failure=snapshot_path_error,
            )
            directory_descriptors.append(parent_descriptor)
            directory_observations.append(directory_fingerprint(parent_status))
        descriptor, opened_status = open_regular_file_component(
            parent_descriptor=parent_descriptor,
            component=relative_path[-1],
            path=display_path,
            on_failure=snapshot_path_error,
        )
        stream = os.fdopen(descriptor, "rb")
        descriptor = -1
        opened_observation = regular_file_fingerprint(opened_status)
        identity = filesystem_identity(opened_status)
        try:
            yield stream, identity
        except BaseException:
            raise
        else:
            final_opened_status = os.fstat(stream.fileno())
            final_directories, final_path_status = _final_relative_status(
                root_descriptor=root_descriptor,
                relative_path=relative_path,
                display_path=display_path,
            )
            if final_directories != tuple(directory_observations):
                raise ValueError(
                    f"file parent path changed while loading: {display_path}"
                )
            require_same_regular_file(
                path=display_path,
                opened_status=final_opened_status,
                path_status=final_path_status,
                on_failure=snapshot_path_error,
            )
            if regular_file_fingerprint(final_opened_status) != opened_observation:
                raise ValueError(f"file changed while loading: {display_path}")
    finally:
        if stream is not None:
            stream.close()
        elif descriptor >= 0:
            os.close(descriptor)
        for directory_descriptor in reversed(directory_descriptors):
            os.close(directory_descriptor)


def _final_relative_status(
    *,
    root_descriptor: int,
    relative_path: tuple[str, ...],
    display_path: Path,
) -> tuple[tuple[tuple[int, ...], ...], os.stat_result]:
    descriptors: list[int] = []
    observations = [directory_fingerprint(os.fstat(root_descriptor))]
    parent_descriptor = root_descriptor
    try:
        for component in relative_path[:-1]:
            parent_descriptor, status = open_directory_component(
                parent_descriptor=parent_descriptor,
                component=component,
                path=display_path,
                on_failure=snapshot_path_error,
            )
            descriptors.append(parent_descriptor)
            observations.append(directory_fingerprint(status))
        path_status = path_component_status(
            parent_descriptor=parent_descriptor,
            component=relative_path[-1],
            path=display_path,
            on_failure=snapshot_path_error,
        )
        return tuple(observations), path_status
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
