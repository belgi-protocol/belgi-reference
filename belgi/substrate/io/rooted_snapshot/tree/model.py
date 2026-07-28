"""Values and failure types for complete rooted-tree snapshots."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import BinaryIO, Protocol, TypeAlias

from belgi.substrate.io.rooted import FilesystemIdentity

__all__ = [
    "RootedTreeDirectoryDescendantPredicate",
    "RootedTreeEntry",
    "RootedTreeEntryValidator",
    "RootedTreeFailureKind",
    "RootedTreeLimits",
    "RootedTreeNodeFact",
    "RootedTreeNodeKind",
    "RootedTreePlatformBackend",
    "RootedTreePlatformSession",
    "RootedTreeSnapshot",
]


class RootedTreeFailureKind(Enum):
    INVALID_ENTRY_NAME = "invalid-entry-name"
    UNSUPPORTED_ENTRY_TYPE = "unsupported-entry-type"
    DIRECTORY_ENTRY_COUNT = "directory-entry-count"
    MEMBER_COUNT = "member-count"
    MEMBER_SIZE = "member-size"
    TOTAL_SIZE = "total-size"
    MUTATED = "mutated"


class RootedTreeNodeKind(Enum):
    DIRECTORY = "directory"
    REGULAR_FILE = "regular-file"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True, slots=True, kw_only=True)
class RootedTreeLimits:
    directory_entry_count: int
    member_count: int
    member_bytes: int
    total_member_bytes: int
    path_segments: int
    path_segment_bytes: int
    path_bytes: int


@dataclass(frozen=True, slots=True, kw_only=True)
class RootedTreeNodeFact:
    relative_path: str
    identity: FilesystemIdentity
    kind: RootedTreeNodeKind
    size: int
    link_count: int
    observation: tuple[object, ...]


RootedTreeEntryValidator: TypeAlias = Callable[[tuple[RootedTreeNodeFact, ...]], None]
RootedTreeDirectoryDescendantPredicate: TypeAlias = Callable[[RootedTreeNodeFact], bool]


class RootedTreePlatformSession(Protocol):
    def root_fact(self) -> RootedTreeNodeFact: ...

    def directory_entries(
        self,
        *,
        relative_directory: tuple[str, ...],
        maximum_entries: int,
        maximum_candidate_members: int,
    ) -> tuple[RootedTreeNodeFact, ...]: ...

    def open_binary_file(
        self,
        *,
        relative_path: tuple[str, ...],
    ) -> AbstractContextManager[tuple[BinaryIO, FilesystemIdentity]]: ...


class RootedTreePlatformBackend(Protocol):
    def open_session(
        self,
        root: Path,
    ) -> AbstractContextManager[RootedTreePlatformSession]: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class RootedTreeEntry:
    relative_path: str
    octets: bytes


@dataclass(frozen=True, slots=True, kw_only=True)
class RootedTreeSnapshot:
    entries: tuple[RootedTreeEntry, ...]
