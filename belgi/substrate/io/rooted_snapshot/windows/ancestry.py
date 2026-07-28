"""Held Windows capability for one reparse-free absolute root ancestry."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from belgi.substrate.io.access import lexical_absolute_path
from belgi.substrate.io.rooted_snapshot.tree.exceptions import RootedTreeError
from belgi.substrate.io.rooted_snapshot.tree.model import RootedTreeFailureKind
from belgi.substrate.io.windows.access import WindowsAccess, WindowsEntryKind
from belgi.substrate.io.windows.authentication import (
    WindowsDirectoryAuthentication,
    capture_windows_directory_authentication,
)
from belgi.substrate.io.windows.file_info import query_info
from belgi.substrate.io.windows.handle import WindowsHandle, close_windows_handles
from belgi.substrate.io.windows.path_open import (
    open_relative,
    open_windows_root_directory,
)

__all__ = ["WindowsRootedTreeAncestry", "open_windows_rooted_tree_ancestry"]


@dataclass(frozen=True, slots=True, kw_only=True)
class WindowsRootedTreeAncestry:
    root: Path
    handles: tuple[WindowsHandle, ...]
    observations: tuple[WindowsDirectoryAuthentication, ...]

    @property
    def root_handle(self) -> WindowsHandle:
        return self.handles[-1]

    def require_current(self) -> None:
        held = tuple(
            _windows_ancestry_directory_authentication(handle)
            for handle in self.handles
        )
        if held != self.observations:
            raise ValueError(
                f"root ancestry changed during bounded reading: {self.root}"
            )
        try:
            _root, reopened = _open_windows_absolute_directory_chain(
                self.root,
                access=WindowsAccess.READ_SECURITY,
            )
        except (OSError, ValueError) as exc:
            raise ValueError(
                f"root ancestry changed during bounded reading: {self.root}"
            ) from exc
        try:
            reopened_observations = tuple(
                _windows_ancestry_directory_authentication(handle)
                for handle in reopened
            )
            if reopened_observations != self.observations:
                raise ValueError(
                    f"root ancestry changed during bounded reading: {self.root}"
                )
        finally:
            close_windows_handles(reopened)

    def close(self) -> None:
        close_windows_handles(self.handles)


def _windows_ancestry_directory_authentication(
    handle: WindowsHandle,
) -> WindowsDirectoryAuthentication:
    _info, _security, observation = capture_windows_directory_authentication(handle)
    return observation


@contextmanager
def open_windows_rooted_tree_ancestry(
    root: Path,
) -> Iterator[WindowsRootedTreeAncestry]:
    absolute_root, handles = _open_windows_absolute_directory_chain(
        root,
        access=WindowsAccess.READ_SECURITY,
    )
    try:
        ancestry = WindowsRootedTreeAncestry(
            root=absolute_root,
            handles=tuple(handles),
            observations=tuple(
                _windows_ancestry_directory_authentication(handle) for handle in handles
            ),
        )
        try:
            yield ancestry
        except BaseException:
            raise
        else:
            ancestry.require_current()
    finally:
        close_windows_handles(handles)


def _open_windows_absolute_directory_chain(
    path: Path,
    *,
    access: WindowsAccess,
) -> tuple[Path, list[WindowsHandle]]:
    absolute_path = lexical_absolute_path(path)
    if not absolute_path.anchor:
        raise ValueError(f"Windows rooted path must be absolute: {absolute_path}")
    handles: list[WindowsHandle] = []
    try:
        handles.append(
            open_windows_root_directory(
                Path(absolute_path.anchor),
                access=access,
            )
        )
        components = absolute_path.parts[1:]
        for index, component in enumerate(components):
            try:
                handle = open_relative(
                    handles[-1],
                    component,
                    kind=WindowsEntryKind.DIRECTORY,
                    access=access,
                )
            except OSError as directory_error:
                if index == len(components) - 1:
                    _raise_if_windows_root_is_not_directory(
                        parent=handles[-1],
                        component=component,
                        access=access,
                    )
                raise directory_error
            handles.append(handle)
        return absolute_path, handles
    except BaseException:
        close_windows_handles(handles)
        raise


def _raise_if_windows_root_is_not_directory(
    *,
    parent: WindowsHandle,
    component: str,
    access: WindowsAccess,
) -> None:
    root_handle = open_relative(
        parent,
        component,
        kind=WindowsEntryKind.ANY,
        access=access,
    )
    try:
        if not query_info(root_handle).is_directory:
            raise RootedTreeError(
                RootedTreeFailureKind.UNSUPPORTED_ENTRY_TYPE,
                "root must be one real directory",
            )
    finally:
        root_handle.close()
