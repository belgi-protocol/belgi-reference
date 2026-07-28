"""Rooted-tree snapshot exceptions."""

from __future__ import annotations

from .model import RootedTreeFailureKind

__all__ = ["RootedTreeError"]


class RootedTreeError(ValueError):
    def __init__(self, kind: RootedTreeFailureKind, message: str) -> None:
        super().__init__(message)
        self.kind = kind
