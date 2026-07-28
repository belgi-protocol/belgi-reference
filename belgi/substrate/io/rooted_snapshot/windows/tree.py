"""Windows session-backed entry observations for complete rooted snapshots."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from typing import BinaryIO

from belgi.substrate.io.exceptions import WindowsReparsePointError
from belgi.substrate.io.rooted import FilesystemIdentity
from belgi.substrate.io.rooted_snapshot.tree.exceptions import RootedTreeError
from belgi.substrate.io.rooted_snapshot.tree.model import (
    RootedTreeFailureKind,
    RootedTreeNodeFact,
    RootedTreeNodeKind,
    RootedTreePlatformBackend,
    RootedTreePlatformSession,
)
from belgi.substrate.io.windows.access import WindowsAccess, WindowsEntryKind
from belgi.substrate.io.windows.directory import iter_directory
from belgi.substrate.io.windows.file_info import WindowsFileInfo, query_info
from belgi.substrate.io.windows.handle import WindowsHandle, close_windows_handles
from belgi.substrate.io.windows.path_open import (
    open_relative,
    open_relative_reparse_point,
)

from .ancestry import (
    WindowsRootedTreeAncestry,
    open_windows_rooted_tree_ancestry,
)
from .tree_file import open_windows_rooted_tree_file

__all__ = ["WindowsRootedTreeBackend"]

_FILE_ATTRIBUTE_DEVICE = 0x00000040


class WindowsRootedTreeBackend:
    @contextmanager
    def open_session(self, root: Path) -> Iterator[RootedTreePlatformSession]:
        with open_windows_rooted_tree_ancestry(root) as ancestry:
            yield _WindowsRootedTreeSession(ancestry)


class _WindowsRootedTreeSession:
    def __init__(self, ancestry: WindowsRootedTreeAncestry) -> None:
        self._ancestry = ancestry

    def root_fact(self) -> RootedTreeNodeFact:
        return _windows_tree_fact(
            query_info(self._ancestry.root_handle),
            relative_path="",
        )

    def directory_entries(
        self,
        *,
        relative_directory: tuple[str, ...],
        maximum_entries: int,
        maximum_candidate_members: int,
    ) -> tuple[RootedTreeNodeFact, ...]:
        handles = _open_relative_windows_directories(
            root_handle=self._ancestry.root_handle,
            components=relative_directory,
        )
        try:
            parent = handles[-1] if handles else self._ancestry.root_handle
            facts: list[RootedTreeNodeFact] = []
            candidate_members = 0
            for name in iter_directory(parent):
                if len(facts) >= maximum_entries:
                    raise RootedTreeError(
                        RootedTreeFailureKind.DIRECTORY_ENTRY_COUNT,
                        "rooted directory exceeds its directory-entry-count envelope",
                    )
                fact = _windows_relative_tree_fact(
                    parent,
                    name,
                    relative_path="/".join((*relative_directory, name)),
                )
                if fact.kind is not RootedTreeNodeKind.DIRECTORY:
                    if candidate_members >= maximum_candidate_members:
                        raise RootedTreeError(
                            RootedTreeFailureKind.MEMBER_COUNT,
                            "rooted tree exceeds its member-count envelope",
                        )
                    candidate_members += 1
                facts.append(fact)
            return tuple(
                sorted(
                    facts,
                    key=lambda fact: (
                        fact.relative_path.casefold(),
                        fact.relative_path,
                    ),
                )
            )
        finally:
            close_windows_handles(handles)

    def open_binary_file(
        self,
        *,
        relative_path: tuple[str, ...],
    ) -> AbstractContextManager[tuple[BinaryIO, FilesystemIdentity]]:
        return open_windows_rooted_tree_file(
            root_handle=self._ancestry.root_handle,
            relative_path=relative_path,
        )


def _open_relative_windows_directories(
    *,
    root_handle: WindowsHandle,
    components: tuple[str, ...],
) -> list[WindowsHandle]:
    handles: list[WindowsHandle] = []
    parent = root_handle
    try:
        for component in components:
            handle = open_relative(
                parent,
                component,
                kind=WindowsEntryKind.DIRECTORY,
                access=WindowsAccess.INSPECT,
            )
            handles.append(handle)
            parent = handle
        return handles
    except BaseException:
        close_windows_handles(handles)
        raise


def _windows_relative_tree_fact(
    parent: WindowsHandle,
    name: str,
    *,
    relative_path: str,
) -> RootedTreeNodeFact:
    try:
        handle = open_relative(
            parent,
            name,
            kind=WindowsEntryKind.ANY,
            access=WindowsAccess.INSPECT,
        )
    except WindowsReparsePointError:
        handle = open_relative_reparse_point(
            parent,
            name,
            access=WindowsAccess.INSPECT,
        )
    try:
        return _windows_tree_fact(query_info(handle), relative_path=relative_path)
    finally:
        handle.close()


def _windows_tree_fact(
    info: WindowsFileInfo,
    *,
    relative_path: str,
) -> RootedTreeNodeFact:
    if info.is_reparse_point:
        kind = RootedTreeNodeKind.UNSUPPORTED
    elif info.is_directory:
        kind = RootedTreeNodeKind.DIRECTORY
    elif info.is_regular_file and not info.attributes & _FILE_ATTRIBUTE_DEVICE:
        kind = RootedTreeNodeKind.REGULAR_FILE
    else:
        kind = RootedTreeNodeKind.UNSUPPORTED
    return RootedTreeNodeFact(
        relative_path=relative_path,
        identity=info.identity,
        kind=kind,
        size=info.end_of_file,
        link_count=info.number_of_links,
        observation=(
            info.identity,
            info.attributes,
            info.reparse_tag,
            info.creation_time,
            info.last_write_time,
            info.change_time,
            info.end_of_file,
            info.number_of_links,
            info.delete_pending,
            info.is_directory,
        ),
    )


_protocol_check: RootedTreePlatformBackend = WindowsRootedTreeBackend()
