"""Shared rooted-path binding policy for POSIX snapshots."""

from __future__ import annotations

from pathlib import Path

from belgi.substrate.io.exceptions import RootedPathSymlinkError
from belgi.substrate.io.posix.capabilities import supports_rooted_paths
from belgi.substrate.io.rooted import RootedPathFailure, rooted_relative_path


def snapshot_path_error(
    failure: RootedPathFailure,
    path: Path,
) -> BaseException:
    if failure is RootedPathFailure.SYMLINK:
        return RootedPathSymlinkError(f"symlink not allowed while loading: {path}")
    if failure is RootedPathFailure.EXPECTED_DIRECTORY:
        return ValueError(f"expected a directory while loading: {path}")
    if failure in {
        RootedPathFailure.DIRECTORY_PATH_NOT_DIRECTORY,
        RootedPathFailure.DIRECTORY_CHANGED,
    }:
        return ValueError(f"directory path changed while loading: {path}")
    if failure is RootedPathFailure.EXPECTED_REGULAR_FILE:
        return ValueError(f"expected a regular file: {path}")
    if failure in {
        RootedPathFailure.FILE_PATH_NOT_REGULAR_FILE,
        RootedPathFailure.FILE_CHANGED,
    }:
        return ValueError(f"file path changed while loading: {path}")
    if failure is RootedPathFailure.PATH_APPEARED:
        return ValueError(f"path appeared while loading an absence snapshot: {path}")
    return AssertionError(f"unexpected snapshot rooted-path failure: {failure.value}")


def snapshot_relative_path(*, root: Path, path: Path) -> tuple[Path, Path]:
    return rooted_relative_path(
        root=root,
        path=path,
        label="snapshot path",
        entry_label="entry",
    )


def require_anchored_open_support() -> None:
    if not supports_rooted_paths():
        raise RuntimeError(
            "anchored no-follow snapshots are unsupported on this platform"
        )


__all__ = [
    "require_anchored_open_support",
    "snapshot_path_error",
    "snapshot_relative_path",
]
