"""Pure Git object-identity grammar."""

from __future__ import annotations

import re

_SHA1_40_RE = re.compile(r"^[0-9a-f]{40}$")
_FULL_GIT_OBJECT_ID_RE = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")


def is_full_git_object_id(value: object) -> bool:
    return (
        isinstance(value, str) and _FULL_GIT_OBJECT_ID_RE.fullmatch(value) is not None
    )


def require_commit_sha40(value: str, *, label: str) -> str:
    sha = _normalized_sha40(value)
    if sha is None:
        raise ValueError(f"{label} must be a stable 40-hex commit SHA")
    return sha


def require_tree_sha40(value: str, *, label: str) -> str:
    sha = _normalized_sha40(value)
    if sha is None:
        raise ValueError(f"unexpected {label}: {value!r}")
    return sha


def _normalized_sha40(value: str) -> str | None:
    sha = str(value or "").strip().lower()
    return sha if _SHA1_40_RE.fullmatch(sha) is not None else None


__all__ = [
    "is_full_git_object_id",
    "require_commit_sha40",
    "require_tree_sha40",
]
