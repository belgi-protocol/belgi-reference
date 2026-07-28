from __future__ import annotations

import os
from pathlib import Path

__all__ = [
    "directory_supports_state_writes",
    "file_supports_state_writes",
    "filesystem_ignores_case",
    "lexical_absolute_path",
    "paths_share_filesystem_identity",
]


def directory_supports_state_writes(path: Path) -> bool:
    return path.is_dir() and os.access(path, os.W_OK | os.X_OK)


def file_supports_state_writes(path: Path) -> bool:
    return path.is_file() and os.access(path, os.W_OK)


def filesystem_ignores_case(path: Path) -> bool:
    if not path.exists() and not path.is_symlink():
        raise FileNotFoundError(path)
    alias_name = path.name.swapcase()
    if alias_name == path.name:
        raise ValueError(f"path has no case-distinct alias: {path}")
    alias = path.with_name(alias_name)
    try:
        return alias.exists() and path.samefile(alias)
    except OSError as exc:
        raise ValueError(
            f"filesystem case identity cannot be inspected: {path}"
        ) from exc


def lexical_absolute_path(path: Path) -> Path:
    return Path(os.path.abspath(path))


def paths_share_filesystem_identity(left: Path, right: Path) -> bool:
    return left.samefile(right)
