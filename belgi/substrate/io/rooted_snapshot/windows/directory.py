from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from belgi.substrate.io.access import lexical_absolute_path
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
    capture_windows_directory_authentication,
)
from belgi.substrate.io.windows.file_info import query_info
from belgi.substrate.io.windows.handle import WindowsHandle, close_windows_handles
from belgi.substrate.io.windows.path_open import (
    open_relative,
    open_windows_root_directory,
    relative_entry_exists,
)

from .binding import (
    open_windows_directory_chain,
    require_windows_directory,
    verify_windows_directory_chain,
    windows_snapshot_relative_path,
)

__all__ = [
    "open_windows_directory_snapshot",
    "open_windows_path_absence_snapshot",
]


@contextmanager
def open_windows_directory_snapshot(
    path: Path,
    *,
    root: Path,
) -> Iterator[tuple[FilesystemIdentity, bool]]:
    absolute_root = lexical_absolute_path(root)
    absolute_path = lexical_absolute_path(path)
    if absolute_path == absolute_root:
        relative_path = Path()
    else:
        absolute_root, relative_path = windows_snapshot_relative_path(
            root=absolute_root,
            path=absolute_path,
        )

    directory_handles: list[WindowsHandle] = []
    try:
        directory_handles, directory_authentications = open_windows_directory_chain(
            root=absolute_root,
            components=relative_path.parts,
            path=path,
        )
        target_info = query_info(directory_handles[-1])
        require_windows_directory(target_info, path=path)
        identity = target_info.identity
        supports_state_writes = _windows_directory_supports_state_writes(
            root=absolute_root,
            parent_handle=(directory_handles[-2] if relative_path.parts else None),
            component=(relative_path.parts[-1] if relative_path.parts else None),
            expected_identity=identity,
            path=path,
        )
        try:
            yield identity, supports_state_writes
        finally:
            final_handles = verify_windows_directory_chain(
                root=absolute_root,
                root_handle=directory_handles[0],
                components=relative_path.parts,
                held_handles=directory_handles,
                expected_authentications=directory_authentications,
                path=path,
                changed_message=f"directory path changed while loading: {path}",
            )
            try:
                final_supports_state_writes = _windows_directory_supports_state_writes(
                    root=absolute_root,
                    parent_handle=(final_handles[-2] if relative_path.parts else None),
                    component=(
                        relative_path.parts[-1] if relative_path.parts else None
                    ),
                    expected_identity=identity,
                    path=path,
                )
            finally:
                close_windows_handles(final_handles[1:])
            if final_supports_state_writes != supports_state_writes:
                raise ValueError(f"directory access changed while loading: {path}")
    except WindowsReparsePointError as exc:
        raise RootedPathSymlinkError(
            f"symlink not allowed while loading: {path}"
        ) from exc
    finally:
        close_windows_handles(directory_handles)


def _windows_directory_supports_state_writes(
    *,
    root: Path,
    parent_handle: WindowsHandle | None,
    component: str | None,
    expected_identity: FilesystemIdentity,
    path: Path,
) -> bool:
    try:
        write_handle = _open_directory_for_access(
            root=root,
            parent_handle=parent_handle,
            component=component,
            access=WindowsAccess.DIRECTORY_WRITE,
        )
    except OSError as error:
        if not is_access_unavailable_error(error):
            raise
        inspection_handle = _open_directory_for_access(
            root=root,
            parent_handle=parent_handle,
            component=component,
            access=WindowsAccess.INSPECT,
        )
        try:
            inspected_info = query_info(inspection_handle)
            require_windows_directory(inspected_info, path=path)
            if inspected_info.identity != expected_identity:
                raise ValueError(
                    f"directory path changed while checking writes: {path}"
                )
        finally:
            inspection_handle.close()
        return False
    try:
        write_info = query_info(write_handle)
        require_windows_directory(write_info, path=path)
        if write_info.identity != expected_identity:
            raise ValueError(f"directory path changed while checking writes: {path}")
        return True
    finally:
        write_handle.close()


def _require_windows_relative_entry_absent(
    parent_handle: WindowsHandle,
    component: str,
    *,
    path: Path,
) -> None:
    if relative_entry_exists(parent_handle, component):
        raise ValueError(f"path appeared while loading an absence snapshot: {path}")


def _open_directory_for_access(
    *,
    root: Path,
    parent_handle: WindowsHandle | None,
    component: str | None,
    access: WindowsAccess,
) -> WindowsHandle:
    if parent_handle is None:
        if component is not None:
            raise AssertionError("root directory cannot have a relative component")
        return open_windows_root_directory(root, access=access)
    if component is None:
        raise AssertionError("directory component is required with a parent")
    return open_relative(
        parent_handle,
        component,
        kind=WindowsEntryKind.DIRECTORY,
        access=access,
    )


@contextmanager
def open_windows_path_absence_snapshot(
    path: Path,
    *,
    root: Path,
) -> Iterator[tuple[Path, bool]]:
    absolute_root, relative_path = windows_snapshot_relative_path(root=root, path=path)
    directory_handles: list[WindowsHandle] = []
    try:
        root_handle = open_windows_root_directory(
            absolute_root,
            access=WindowsAccess.READ_SECURITY,
        )
        directory_handles.append(root_handle)
        root_info, _root_security, root_authentication = (
            capture_windows_directory_authentication(root_handle)
        )
        require_windows_directory(root_info, path=absolute_root)
        directory_authentications = [root_authentication]

        parent_handle = root_handle
        existing_parent_path = absolute_root
        absent_component = relative_path.parts[-1]
        for component in relative_path.parts[:-1]:
            if not relative_entry_exists(parent_handle, component):
                absent_component = component
                break
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
            directory_handles.append(child_handle)
            directory_authentications.append(child_authentication)
            parent_handle = child_handle
            existing_parent_path /= component
        else:
            _require_windows_relative_entry_absent(
                parent_handle,
                absent_component,
                path=path,
            )

        parent_identity = query_info(parent_handle).identity
        parent_component_count = len(directory_handles) - 1
        existing_parent_supports_state_writes = (
            _windows_directory_supports_state_writes(
                root=absolute_root,
                parent_handle=(
                    directory_handles[-2] if parent_component_count else None
                ),
                component=(
                    relative_path.parts[parent_component_count - 1]
                    if parent_component_count
                    else None
                ),
                expected_identity=parent_identity,
                path=existing_parent_path,
            )
        )
        try:
            yield existing_parent_path, existing_parent_supports_state_writes
        finally:
            parent_components = relative_path.parts[:parent_component_count]
            final_handles = verify_windows_directory_chain(
                root=absolute_root,
                root_handle=root_handle,
                components=parent_components,
                held_handles=directory_handles,
                expected_authentications=tuple(directory_authentications),
                path=path,
                changed_message=f"path parent changed while loading: {path}",
            )
            try:
                _require_windows_relative_entry_absent(
                    final_handles[-1],
                    absent_component,
                    path=path,
                )
                final_parent_supports_state_writes = (
                    _windows_directory_supports_state_writes(
                        root=absolute_root,
                        parent_handle=(
                            final_handles[-2] if parent_component_count else None
                        ),
                        component=(
                            parent_components[-1] if parent_component_count else None
                        ),
                        expected_identity=parent_identity,
                        path=existing_parent_path,
                    )
                )
            finally:
                close_windows_handles(final_handles[1:])
            if (
                final_parent_supports_state_writes
                != existing_parent_supports_state_writes
            ):
                raise ValueError(f"path parent access changed while loading: {path}")
    except WindowsReparsePointError as exc:
        raise RootedPathSymlinkError(
            f"symlink not allowed while loading: {path}"
        ) from exc
    finally:
        close_windows_handles(directory_handles)
