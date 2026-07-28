from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO

from belgi.substrate.io.exceptions import (
    RootedPathSymlinkError,
    WindowsReparsePointError,
)
from belgi.substrate.io.rooted import FilesystemIdentity
from belgi.substrate.io.windows.access import (
    WindowsAccess,
    WindowsEntryKind,
    is_access_unavailable_error,
)
from belgi.substrate.io.windows.authentication import (
    windows_regular_file_authentication,
)
from belgi.substrate.io.windows.file_info import query_info
from belgi.substrate.io.windows.handle import WindowsHandle, close_windows_handles
from belgi.substrate.io.windows.path_open import (
    open_relative,
)
from belgi.substrate.io.windows.stream import (
    binary_stream,
    query_info_for_file_descriptor,
)

from .binding import (
    open_windows_directory_chain,
    require_windows_regular_file,
    verify_windows_binary_file_binding,
    verify_windows_regular_file_identity_binding,
    windows_snapshot_relative_path,
)

__all__ = [
    "open_windows_binary_file_snapshot",
    "windows_rooted_regular_file_supports_state_writes",
]


@contextmanager
def open_windows_binary_file_snapshot(
    path: Path,
    *,
    root: Path,
) -> Iterator[tuple[BinaryIO, FilesystemIdentity]]:
    absolute_root, relative_path = windows_snapshot_relative_path(root=root, path=path)
    directory_handles: list[WindowsHandle] = []
    file_handle: WindowsHandle | None = None
    stream: BinaryIO | None = None
    try:
        directory_handles, directory_authentications = open_windows_directory_chain(
            root=absolute_root,
            components=relative_path.parts[:-1],
            path=path,
        )
        file_handle = open_relative(
            directory_handles[-1],
            relative_path.parts[-1],
            kind=WindowsEntryKind.REGULAR_FILE,
            access=WindowsAccess.READ_DATA,
        )
        opened_info = query_info(file_handle)
        require_windows_regular_file(opened_info, path=path)
        opened_authentication = windows_regular_file_authentication(opened_info)
        stream = binary_stream(file_handle)
        try:
            yield stream, opened_info.identity
        finally:
            final_opened_info = query_info_for_file_descriptor(stream.fileno())
            require_windows_regular_file(final_opened_info, path=path)
            if (
                windows_regular_file_authentication(final_opened_info)
                != opened_authentication
            ):
                raise ValueError(f"file changed while loading: {path}")
            verify_windows_binary_file_binding(
                root=absolute_root,
                root_handle=directory_handles[0],
                relative_path=relative_path,
                held_directory_handles=directory_handles,
                expected_directory_authentications=directory_authentications,
                expected_file_authentication=opened_authentication,
                path=path,
            )
    except WindowsReparsePointError as exc:
        raise RootedPathSymlinkError(
            f"symlink not allowed while loading: {path}"
        ) from exc
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


def windows_rooted_regular_file_supports_state_writes(
    path: Path,
    *,
    root: Path,
    expected_identity: FilesystemIdentity,
) -> bool:
    absolute_root, relative_path = windows_snapshot_relative_path(root=root, path=path)
    directory_handles: list[WindowsHandle] = []
    inspection_handle: WindowsHandle | None = None
    write_handle: WindowsHandle | None = None
    try:
        directory_handles, directory_authentications = open_windows_directory_chain(
            root=absolute_root,
            components=relative_path.parts[:-1],
            path=path,
        )
        parent_handle = directory_handles[-1]
        component = relative_path.parts[-1]
        inspection_handle = open_relative(
            parent_handle,
            component,
            kind=WindowsEntryKind.REGULAR_FILE,
        )
        inspected_info = query_info(inspection_handle)
        require_windows_regular_file(inspected_info, path=path)
        if inspected_info.identity != expected_identity:
            raise ValueError(f"file path changed while checking writes: {path}")
        try:
            write_handle = open_relative(
                parent_handle,
                component,
                kind=WindowsEntryKind.REGULAR_FILE,
                access=WindowsAccess.WRITE_DATA,
            )
        except OSError as exc:
            if not is_access_unavailable_error(exc):
                raise
            result = False
        else:
            write_info = query_info(write_handle)
            require_windows_regular_file(write_info, path=path)
            if write_info.identity != expected_identity:
                raise ValueError(f"file path changed while checking writes: {path}")
            result = True

        verify_windows_regular_file_identity_binding(
            root=absolute_root,
            root_handle=directory_handles[0],
            relative_path=relative_path,
            held_directory_handles=directory_handles,
            expected_directory_authentications=directory_authentications,
            expected_identity=expected_identity,
            path=path,
        )
        return result
    except WindowsReparsePointError as exc:
        raise RootedPathSymlinkError(
            f"symlink not allowed while checking writes: {path}"
        ) from exc
    finally:
        try:
            if write_handle is not None:
                write_handle.close()
        finally:
            try:
                if inspection_handle is not None:
                    inspection_handle.close()
            finally:
                close_windows_handles(directory_handles)
