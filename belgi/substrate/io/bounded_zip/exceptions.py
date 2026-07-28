"""Bounded ZIP mechanism exceptions."""

from __future__ import annotations

from enum import Enum

__all__ = ["BoundedZipError", "ZipFailureKind"]


class ZipFailureKind(Enum):
    OUTER_SIZE = "outer-size"
    MALFORMED = "malformed"
    UNSUPPORTED_FEATURE = "unsupported-feature"
    ENTRY_COUNT = "entry-count"
    MEMBER_SIZE = "member-size"
    TOTAL_SIZE = "total-size"
    STREAM_MISMATCH = "stream-mismatch"


class BoundedZipError(ValueError):
    def __init__(self, kind: ZipFailureKind, message: str) -> None:
        super().__init__(message)
        self.kind = kind
