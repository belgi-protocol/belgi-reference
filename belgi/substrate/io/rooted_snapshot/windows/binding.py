from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from belgi.substrate.io.exceptions import RootedPathSymlinkError
from belgi.substrate.io.rooted import FilesystemIdentity, rooted_relative_path
from belgi.substrate.io.windows.access import WindowsAccess, WindowsEntryKind
from belgi.substrate.io.windows.authentication import (
    WindowsDirectoryAuthentication,
    WindowsRegularFileAuthentication,
    capture_windows_directory_authentication,
    windows_regular_file_authentication,
)
from belgi.substrate.io.windows.file_info import WindowsFileInfo, query_info
from belgi.substrate.io.windows.handle import WindowsHandle, close_windows_handles
from belgi.substrate.io.windows.path_open import (
    open_relative,
    open_windows_root_directory,
)

__all__ = [
    "open_windows_directory_chain",
    "require_windows_directory",
    "require_windows_regular_file",
    "verify_windows_binary_file_binding",
    "verify_windows_directory_chain",
    "verify_windows_regular_file_identity_binding",
    "windows_snapshot_relative_path",
]


def windows_snapshot_relative_path(*, root: Path, path: Path) -> tuple[Path, Path]:
    return rooted_relative_path(
        root=root,
        path=path,
        label="snapshot path",
        entry_label="entry",
    )


def open_windows_directory_chain(
    *,
    root: Path,
    components: Sequence[str],
    path: Path,
) -> tuple[list[WindowsHandle], tuple[WindowsDirectoryAuthentication, ...]]:
    handles: list[WindowsHandle] = []
    try:
        root_handle = open_windows_root_directory(
            root,
            access=WindowsAccess.READ_SECURITY,
        )
        handles.append(root_handle)
        root_info, _root_security, root_authentication = (
            capture_windows_directory_authentication(root_handle)
        )
        require_windows_directory(root_info, path=root)
        authentications = [root_authentication]
        parent_handle = root_handle
        for component in components:
            child_handle = open_relative(
                parent_handle,
                component,
                kind=WindowsEntryKind.DIRECTORY,
                access=WindowsAccess.READ_SECURITY,
            )
            try:
                child_info, _child_security, child_authentication = (
                    capture_windows_directory_authentication(child_handle)
                )
                require_windows_directory(child_info, path=path)
            except BaseException:
                close_windows_handles((child_handle,))
                raise
            handles.append(child_handle)
            authentications.append(child_authentication)
            parent_handle = child_handle
        return handles, tuple(authentications)
    except BaseException:
        close_windows_handles(handles)
        raise


def verify_windows_directory_chain(
    *,
    root: Path,
    root_handle: WindowsHandle,
    components: Sequence[str],
    held_handles: Sequence[WindowsHandle],
    expected_authentications: Sequence[WindowsDirectoryAuthentication],
    path: Path,
    changed_message: str,
) -> list[WindowsHandle]:
    held_authentications = tuple(
        _windows_snapshot_directory_binding(handle, path=path)
        for handle in held_handles
    )
    if held_authentications != tuple(expected_authentications):
        raise ValueError(changed_message)

    final_handles: list[WindowsHandle] = [root_handle]
    try:
        final_authentications = [
            _windows_snapshot_directory_binding(root_handle, path=root)
        ]
        parent_handle = root_handle
        for component in components:
            child_handle = open_relative(
                parent_handle,
                component,
                kind=WindowsEntryKind.DIRECTORY,
                access=WindowsAccess.READ_SECURITY,
            )
            try:
                child_info, _child_security, child_authentication = (
                    capture_windows_directory_authentication(child_handle)
                )
                require_windows_directory(child_info, path=path)
            except BaseException:
                close_windows_handles((child_handle,))
                raise
            final_handles.append(child_handle)
            final_authentications.append(child_authentication)
            parent_handle = child_handle
        if tuple(final_authentications) != tuple(expected_authentications):
            raise ValueError(changed_message)
        _require_absolute_root_binding(
            root=root,
            expected_authentication=expected_authentications[0],
            changed_message=changed_message,
        )
        return final_handles
    except BaseException:
        close_windows_handles(final_handles[1:])
        raise


def verify_windows_binary_file_binding(
    *,
    root: Path,
    root_handle: WindowsHandle,
    relative_path: Path,
    held_directory_handles: Sequence[WindowsHandle],
    expected_directory_authentications: Sequence[WindowsDirectoryAuthentication],
    expected_file_authentication: WindowsRegularFileAuthentication,
    path: Path,
) -> None:
    final_handles = verify_windows_directory_chain(
        root=root,
        root_handle=root_handle,
        components=relative_path.parts[:-1],
        held_handles=held_directory_handles,
        expected_authentications=expected_directory_authentications,
        path=path,
        changed_message=f"file parent path changed while loading: {path}",
    )
    final_file_handle: WindowsHandle | None = None
    try:
        final_file_handle = open_relative(
            final_handles[-1],
            relative_path.parts[-1],
            kind=WindowsEntryKind.REGULAR_FILE,
        )
        final_file_info = query_info(final_file_handle)
        require_windows_regular_file(final_file_info, path=path)
        if (
            windows_regular_file_authentication(final_file_info)
            != expected_file_authentication
        ):
            raise ValueError(f"file path changed while loading: {path}")
    finally:
        try:
            if final_file_handle is not None:
                final_file_handle.close()
        finally:
            close_windows_handles(final_handles[1:])


def verify_windows_regular_file_identity_binding(
    *,
    root: Path,
    root_handle: WindowsHandle,
    relative_path: Path,
    held_directory_handles: Sequence[WindowsHandle],
    expected_directory_authentications: Sequence[WindowsDirectoryAuthentication],
    expected_identity: FilesystemIdentity,
    path: Path,
) -> None:
    changed_message = f"file path changed while checking writes: {path}"
    final_handles = verify_windows_directory_chain(
        root=root,
        root_handle=root_handle,
        components=relative_path.parts[:-1],
        held_handles=held_directory_handles,
        expected_authentications=expected_directory_authentications,
        path=path,
        changed_message=changed_message,
    )
    final_file_handle: WindowsHandle | None = None
    try:
        final_file_handle = open_relative(
            final_handles[-1],
            relative_path.parts[-1],
            kind=WindowsEntryKind.REGULAR_FILE,
        )
        final_file_info = query_info(final_file_handle)
        require_windows_regular_file(final_file_info, path=path)
        if final_file_info.identity != expected_identity:
            raise ValueError(changed_message)
    finally:
        try:
            if final_file_handle is not None:
                final_file_handle.close()
        finally:
            close_windows_handles(final_handles[1:])


def require_windows_directory(info: WindowsFileInfo, *, path: Path) -> None:
    if info.is_reparse_point:
        raise RootedPathSymlinkError(f"symlink not allowed while loading: {path}")
    if info.delete_pending:
        raise ValueError(f"directory path changed while loading: {path}")
    if not info.is_directory:
        raise ValueError(f"expected a directory while loading: {path}")


def require_windows_regular_file(info: WindowsFileInfo, *, path: Path) -> None:
    if info.is_reparse_point:
        raise RootedPathSymlinkError(f"symlink not allowed while loading: {path}")
    if info.delete_pending:
        raise ValueError(f"file path changed while loading: {path}")
    if not info.is_regular_file:
        raise ValueError(f"expected a regular file: {path}")


def _windows_snapshot_directory_binding(
    handle: WindowsHandle,
    *,
    path: Path,
) -> WindowsDirectoryAuthentication:
    info, _security, authentication = capture_windows_directory_authentication(handle)
    require_windows_directory(info, path=path)
    return authentication


def _require_absolute_root_binding(
    *,
    root: Path,
    expected_authentication: WindowsDirectoryAuthentication,
    changed_message: str,
) -> None:
    reopened_root = open_windows_root_directory(
        root,
        access=WindowsAccess.READ_SECURITY,
    )
    try:
        reopened_authentication = _windows_snapshot_directory_binding(
            reopened_root,
            path=root,
        )
        if reopened_authentication != expected_authentication:
            raise ValueError(changed_message)
    finally:
        reopened_root.close()
