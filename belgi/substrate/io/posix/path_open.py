"""No-follow descriptor opening and status traversal for POSIX paths."""

from __future__ import annotations

import os
import stat
from collections.abc import Callable
from pathlib import Path

from belgi.substrate.io.rooted import (
    FilesystemIdentity,
    RootedPathErrorPolicy,
    RootedPathFailure,
)

from .authentication import require_same_directory, require_same_regular_file
from .metadata import filesystem_identity

_O_CLOEXEC = getattr(os, "O_CLOEXEC", 0)
_O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
_O_NONBLOCK = getattr(os, "O_NONBLOCK", 0)
_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)


def open_root_directory(
    root: Path,
    *,
    on_failure: RootedPathErrorPolicy,
) -> tuple[int, os.stat_result]:
    descriptor = os.open(root, _directory_open_flags())
    try:
        opened_status = os.fstat(descriptor)
        require_same_directory(
            path=root,
            opened_status=opened_status,
            path_status=root.lstat(),
            on_failure=on_failure,
        )
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor, opened_status


def nofollow_component_status(
    *,
    parent_descriptor: int,
    component: str,
) -> os.stat_result:
    return os.stat(
        component,
        dir_fd=parent_descriptor,
        follow_symlinks=False,
    )


def path_component_status(
    *,
    parent_descriptor: int,
    component: str,
    path: Path,
    on_failure: RootedPathErrorPolicy,
) -> os.stat_result:
    status = nofollow_component_status(
        parent_descriptor=parent_descriptor,
        component=component,
    )
    if stat.S_ISLNK(status.st_mode):
        raise on_failure(RootedPathFailure.SYMLINK, path)
    return status


def require_path_component_absent(
    *,
    parent_descriptor: int,
    component: str,
    path: Path,
    on_failure: RootedPathErrorPolicy,
) -> None:
    try:
        path_component_status(
            parent_descriptor=parent_descriptor,
            component=component,
            path=path,
            on_failure=on_failure,
        )
    except FileNotFoundError:
        return
    raise on_failure(RootedPathFailure.PATH_APPEARED, path)


def open_directory_component(
    *,
    parent_descriptor: int,
    component: str,
    path: Path,
    on_failure: RootedPathErrorPolicy,
) -> tuple[int, os.stat_result]:
    path_status = path_component_status(
        parent_descriptor=parent_descriptor,
        component=component,
        path=path,
        on_failure=on_failure,
    )
    if not stat.S_ISDIR(path_status.st_mode):
        raise on_failure(RootedPathFailure.EXPECTED_DIRECTORY, path)
    descriptor = os.open(
        component,
        _directory_open_flags(),
        dir_fd=parent_descriptor,
    )
    try:
        opened_status = os.fstat(descriptor)
        require_same_directory(
            path=path,
            opened_status=opened_status,
            path_status=path_status,
            on_failure=on_failure,
        )
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor, opened_status


def open_regular_file_component(
    *,
    parent_descriptor: int,
    component: str,
    path: Path,
    writable: bool = False,
    expected_identity: FilesystemIdentity | None = None,
    on_failure: RootedPathErrorPolicy,
) -> tuple[int, os.stat_result]:
    opened = try_open_regular_file_component(
        parent_descriptor=parent_descriptor,
        component=component,
        path=path,
        writable=writable,
        expected_identity=expected_identity,
        on_failure=on_failure,
        open_unavailable=_never_unavailable,
    )
    assert opened is not None
    return opened


def try_open_regular_file_component(
    *,
    parent_descriptor: int,
    component: str,
    path: Path,
    writable: bool = False,
    expected_identity: FilesystemIdentity | None = None,
    on_failure: RootedPathErrorPolicy,
    open_unavailable: Callable[[OSError], bool],
) -> tuple[int, os.stat_result] | None:
    path_status = path_component_status(
        parent_descriptor=parent_descriptor,
        component=component,
        path=path,
        on_failure=on_failure,
    )
    if not stat.S_ISREG(path_status.st_mode):
        raise on_failure(RootedPathFailure.EXPECTED_REGULAR_FILE, path)
    if (
        expected_identity is not None
        and filesystem_identity(path_status) != expected_identity
    ):
        raise ValueError(f"file path changed while checking writes: {path}")
    try:
        descriptor = os.open(
            component,
            (os.O_WRONLY if writable else os.O_RDONLY)
            | getattr(os, "O_BINARY", 0)
            | _O_CLOEXEC
            | _O_NONBLOCK
            | _O_NOFOLLOW,
            dir_fd=parent_descriptor,
        )
    except OSError as error:
        if open_unavailable(error):
            return None
        raise
    try:
        opened_status = os.fstat(descriptor)
        require_same_regular_file(
            path=path,
            opened_status=opened_status,
            path_status=path_status,
            on_failure=on_failure,
        )
        if (
            expected_identity is not None
            and filesystem_identity(opened_status) != expected_identity
        ):
            raise ValueError(f"file path changed while checking writes: {path}")
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor, opened_status


def _never_unavailable(_error: OSError) -> bool:
    return False


def _directory_open_flags() -> int:
    return os.O_RDONLY | _O_CLOEXEC | _O_DIRECTORY | _O_NOFOLLOW


__all__ = [
    "nofollow_component_status",
    "open_directory_component",
    "open_regular_file_component",
    "open_root_directory",
    "path_component_status",
    "require_path_component_absent",
    "try_open_regular_file_component",
]
