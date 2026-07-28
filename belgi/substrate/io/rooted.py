"""Platform-neutral rooted-path identity and failure vocabulary."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum
from pathlib import Path
from typing import TypeAlias

from .access import lexical_absolute_path

FilesystemIdentity: TypeAlias = tuple[int, int]
PathFingerprint: TypeAlias = tuple[int, ...]


class RootedPathFailure(Enum):
    SYMLINK = "symlink"
    EXPECTED_DIRECTORY = "expected-directory"
    DIRECTORY_PATH_NOT_DIRECTORY = "directory-path-not-directory"
    DIRECTORY_CHANGED = "directory-changed"
    EXPECTED_REGULAR_FILE = "expected-regular-file"
    FILE_PATH_NOT_REGULAR_FILE = "file-path-not-regular-file"
    FILE_CHANGED = "file-changed"
    PATH_APPEARED = "path-appeared"


RootedPathErrorPolicy: TypeAlias = Callable[[RootedPathFailure, Path], BaseException]


def rooted_relative_path(
    *,
    root: Path,
    path: Path,
    label: str,
    entry_label: str,
) -> tuple[Path, Path]:
    absolute_root = lexical_absolute_path(root)
    absolute_path = lexical_absolute_path(path)
    try:
        relative_path = absolute_path.relative_to(absolute_root)
    except ValueError as exc:
        raise ValueError(f"{label} must stay within root: {absolute_path}") from exc
    if relative_path == Path(".") or any(
        part in {"", ".", ".."} for part in relative_path.parts
    ):
        raise ValueError(f"{label} must name a rooted {entry_label}: {absolute_path}")
    return absolute_root, relative_path


__all__ = [
    "FilesystemIdentity",
    "PathFingerprint",
    "RootedPathErrorPolicy",
    "RootedPathFailure",
    "rooted_relative_path",
]
