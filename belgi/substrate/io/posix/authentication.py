"""Identity authentication for descriptor-rooted POSIX entries."""

from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import NoReturn

from belgi.substrate.io.rooted import (
    FilesystemIdentity,
    RootedPathErrorPolicy,
    RootedPathFailure,
)

from .metadata import filesystem_identity, is_directory


def require_same_directory(
    *,
    path: Path,
    opened_status: os.stat_result,
    path_status: os.stat_result,
    on_failure: RootedPathErrorPolicy,
) -> None:
    if not stat.S_ISDIR(opened_status.st_mode):
        _raise_rooted_path_failure(
            failure=RootedPathFailure.EXPECTED_DIRECTORY,
            path=path,
            on_failure=on_failure,
        )
    if stat.S_ISLNK(path_status.st_mode):
        _raise_rooted_path_failure(
            failure=RootedPathFailure.SYMLINK,
            path=path,
            on_failure=on_failure,
        )
    if not stat.S_ISDIR(path_status.st_mode):
        _raise_rooted_path_failure(
            failure=RootedPathFailure.DIRECTORY_PATH_NOT_DIRECTORY,
            path=path,
            on_failure=on_failure,
        )
    if filesystem_identity(opened_status) != filesystem_identity(path_status):
        _raise_rooted_path_failure(
            failure=RootedPathFailure.DIRECTORY_CHANGED,
            path=path,
            on_failure=on_failure,
        )


def require_same_regular_file(
    *,
    path: Path,
    opened_status: os.stat_result,
    path_status: os.stat_result,
    on_failure: RootedPathErrorPolicy,
) -> None:
    if not stat.S_ISREG(opened_status.st_mode):
        _raise_rooted_path_failure(
            failure=RootedPathFailure.EXPECTED_REGULAR_FILE,
            path=path,
            on_failure=on_failure,
        )
    if stat.S_ISLNK(path_status.st_mode):
        _raise_rooted_path_failure(
            failure=RootedPathFailure.SYMLINK,
            path=path,
            on_failure=on_failure,
        )
    if not stat.S_ISREG(path_status.st_mode):
        _raise_rooted_path_failure(
            failure=RootedPathFailure.FILE_PATH_NOT_REGULAR_FILE,
            path=path,
            on_failure=on_failure,
        )
    if filesystem_identity(opened_status) != filesystem_identity(path_status):
        _raise_rooted_path_failure(
            failure=RootedPathFailure.FILE_CHANGED,
            path=path,
            on_failure=on_failure,
        )


def directory_binding_issue(
    *,
    path: Path,
    descriptor: int,
    expected_identity: FilesystemIdentity,
    parent_descriptor: int | None = None,
    component: str | None = None,
) -> str | None:
    try:
        opened_status = os.fstat(descriptor)
        if parent_descriptor is None:
            path_status = path.lstat()
        else:
            if component is None:
                raise ValueError(
                    "a rooted directory component is required with a parent descriptor"
                )
            path_status = os.stat(
                component,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
    except OSError as error:
        return f"directory binding cannot be inspected: {type(error).__name__}: {error}"
    if not is_directory(opened_status):
        return "opened directory identity is no longer a directory"
    if stat.S_ISLNK(path_status.st_mode) or not is_directory(path_status):
        return "expected path no longer names a directory"
    if filesystem_identity(opened_status) != expected_identity:
        return "opened directory identity changed"
    if filesystem_identity(path_status) != expected_identity:
        return "expected path names a different directory identity"
    return None


def _raise_rooted_path_failure(
    *,
    failure: RootedPathFailure,
    path: Path,
    on_failure: RootedPathErrorPolicy,
) -> NoReturn:
    raise on_failure(failure, path)


__all__ = [
    "directory_binding_issue",
    "require_same_directory",
    "require_same_regular_file",
]
