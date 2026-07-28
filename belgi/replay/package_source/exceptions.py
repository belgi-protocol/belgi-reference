"""Replay-package source exceptions."""

from __future__ import annotations

__all__ = [
    "PackageSourceMemberNotFoundError",
    "UnsupportedPackagePathKindError",
]


class PackageSourceMemberNotFoundError(ValueError):
    """Raised when an embedded source has no member with the requested name."""


class UnsupportedPackagePathKindError(ValueError):
    """Raised when a package path is neither a directory nor a regular file."""
