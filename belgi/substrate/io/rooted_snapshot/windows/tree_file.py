"""Regular-file reading relative to one held Windows rooted-tree capability."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO

from belgi.substrate.io.rooted import FilesystemIdentity
from belgi.substrate.io.windows.access import WindowsAccess, WindowsEntryKind
from belgi.substrate.io.windows.authentication import (
    WindowsDirectoryAuthentication,
    WindowsRegularFileAuthentication,
    capture_windows_directory_authentication,
    windows_regular_file_authentication,
)
from belgi.substrate.io.windows.file_info import query_info
from belgi.substrate.io.windows.handle import WindowsHandle, close_windows_handles
from belgi.substrate.io.windows.path_open import open_relative
from belgi.substrate.io.windows.stream import (
    binary_stream,
    query_info_for_file_descriptor,
)

from .binding import require_windows_directory, require_windows_regular_file

__all__ = ["open_windows_rooted_tree_file"]


@contextmanager
def open_windows_rooted_tree_file(
    *,
    root_handle: WindowsHandle,
    relative_path: tuple[str, ...],
) -> Iterator[tuple[BinaryIO, FilesystemIdentity]]:
    if not relative_path:
        raise ValueError("rooted tree file path must not be empty")
    display_path = Path(*relative_path)
    directory_handles: list[WindowsHandle] = []
    file_handle: WindowsHandle | None = None
    stream: BinaryIO | None = None
    try:
        directory_handles, directory_observations = _open_relative_directories(
            root_handle=root_handle,
            components=relative_path[:-1],
            display_path=display_path,
        )
        parent = directory_handles[-1] if directory_handles else root_handle
        file_handle = open_relative(
            parent,
            relative_path[-1],
            kind=WindowsEntryKind.REGULAR_FILE,
            access=WindowsAccess.READ_DATA,
        )
        opened_info = query_info(file_handle)
        require_windows_regular_file(opened_info, path=display_path)
        opened_observation = windows_regular_file_authentication(opened_info)
        stream = binary_stream(file_handle)
        try:
            yield stream, opened_info.identity
        except BaseException:
            raise
        else:
            final_info = query_info_for_file_descriptor(stream.fileno())
            require_windows_regular_file(final_info, path=display_path)
            if windows_regular_file_authentication(final_info) != opened_observation:
                raise ValueError(f"file changed while loading: {display_path}")
            _verify_relative_binding(
                root_handle=root_handle,
                relative_path=relative_path,
                expected_directories=directory_observations,
                expected_file=opened_observation,
                display_path=display_path,
            )
    finally:
        try:
            if stream is not None:
                stream.close()
        finally:
            try:
                if file_handle is not None and not file_handle.closed:
                    file_handle.close()
            finally:
                close_windows_handles(directory_handles)


def _open_relative_directories(
    *,
    root_handle: WindowsHandle,
    components: tuple[str, ...],
    display_path: Path,
) -> tuple[list[WindowsHandle], tuple[WindowsDirectoryAuthentication, ...]]:
    handles: list[WindowsHandle] = []
    observations: list[WindowsDirectoryAuthentication] = []
    parent = root_handle
    try:
        for component in components:
            handle = open_relative(
                parent,
                component,
                kind=WindowsEntryKind.DIRECTORY,
                access=WindowsAccess.READ_SECURITY,
            )
            try:
                info, _security, observation = capture_windows_directory_authentication(
                    handle
                )
                require_windows_directory(info, path=display_path)
            except BaseException:
                handle.close()
                raise
            handles.append(handle)
            observations.append(observation)
            parent = handle
        return handles, tuple(observations)
    except BaseException:
        close_windows_handles(handles)
        raise


def _verify_relative_binding(
    *,
    root_handle: WindowsHandle,
    relative_path: tuple[str, ...],
    expected_directories: tuple[WindowsDirectoryAuthentication, ...],
    expected_file: WindowsRegularFileAuthentication,
    display_path: Path,
) -> None:
    handles, observations = _open_relative_directories(
        root_handle=root_handle,
        components=relative_path[:-1],
        display_path=display_path,
    )
    final_file: WindowsHandle | None = None
    try:
        if observations != expected_directories:
            raise ValueError(f"file parent path changed while loading: {display_path}")
        parent = handles[-1] if handles else root_handle
        final_file = open_relative(
            parent,
            relative_path[-1],
            kind=WindowsEntryKind.REGULAR_FILE,
        )
        final_info = query_info(final_file)
        require_windows_regular_file(final_info, path=display_path)
        if windows_regular_file_authentication(final_info) != expected_file:
            raise ValueError(f"file path changed while loading: {display_path}")
    finally:
        if final_file is not None:
            final_file.close()
        close_windows_handles(handles)
