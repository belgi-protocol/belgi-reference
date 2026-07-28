"""POSIX session-backed entry observations for complete rooted snapshots."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
from typing import BinaryIO

from belgi.substrate.io.posix.metadata import snapshot_node_metadata
from belgi.substrate.io.posix.path_open import (
    open_directory_component,
)
from belgi.substrate.io.rooted import FilesystemIdentity
from belgi.substrate.io.rooted_snapshot.tree.exceptions import RootedTreeError
from belgi.substrate.io.rooted_snapshot.tree.model import (
    RootedTreeFailureKind,
    RootedTreeNodeFact,
    RootedTreeNodeKind,
    RootedTreePlatformBackend,
    RootedTreePlatformSession,
)

from .ancestry import (
    PosixRootedTreeAncestry,
    open_posix_rooted_tree_ancestry,
)
from .binding import require_anchored_open_support, snapshot_path_error
from .tree_file import open_posix_rooted_tree_file

__all__ = ["PosixRootedTreeBackend"]


class PosixRootedTreeBackend:
    @contextmanager
    def open_session(self, root: Path) -> Iterator[RootedTreePlatformSession]:
        require_anchored_open_support()
        with open_posix_rooted_tree_ancestry(root) as ancestry:
            yield _PosixRootedTreeSession(ancestry)


class _PosixRootedTreeSession:
    def __init__(self, ancestry: PosixRootedTreeAncestry) -> None:
        self._ancestry = ancestry

    def root_fact(self) -> RootedTreeNodeFact:
        return _posix_tree_fact(
            os.fstat(self._ancestry.root_descriptor),
            relative_path="",
        )

    def directory_entries(
        self,
        *,
        relative_directory: tuple[str, ...],
        maximum_entries: int,
        maximum_candidate_members: int,
    ) -> tuple[RootedTreeNodeFact, ...]:
        descriptors = _open_relative_directory_chain(
            root_descriptor=self._ancestry.root_descriptor,
            relative_directory=relative_directory,
        )
        parent_descriptor = (
            descriptors[-1] if descriptors else self._ancestry.root_descriptor
        )
        try:
            facts: list[RootedTreeNodeFact] = []
            candidate_members = 0
            with os.scandir(parent_descriptor) as entries:
                for entry in entries:
                    if len(facts) >= maximum_entries:
                        raise RootedTreeError(
                            RootedTreeFailureKind.DIRECTORY_ENTRY_COUNT,
                            "rooted directory exceeds its directory-entry-count envelope",
                        )
                    fact = _posix_tree_fact(
                        entry.stat(follow_symlinks=False),
                        relative_path="/".join((*relative_directory, entry.name)),
                    )
                    if fact.kind is not RootedTreeNodeKind.DIRECTORY:
                        if candidate_members >= maximum_candidate_members:
                            raise RootedTreeError(
                                RootedTreeFailureKind.MEMBER_COUNT,
                                "rooted tree exceeds its member-count envelope",
                            )
                        candidate_members += 1
                    facts.append(fact)
            return tuple(sorted(facts, key=lambda fact: fact.relative_path))
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)

    def open_binary_file(
        self,
        *,
        relative_path: tuple[str, ...],
    ) -> AbstractContextManager[tuple[BinaryIO, FilesystemIdentity]]:
        return open_posix_rooted_tree_file(
            root_descriptor=self._ancestry.root_descriptor,
            relative_path=relative_path,
        )


def _open_relative_directory_chain(
    *,
    root_descriptor: int,
    relative_directory: tuple[str, ...],
) -> list[int]:
    descriptors: list[int] = []
    parent_descriptor = root_descriptor
    try:
        for component in relative_directory:
            descriptor, _status = open_directory_component(
                parent_descriptor=parent_descriptor,
                component=component,
                path=Path(*relative_directory),
                on_failure=snapshot_path_error,
            )
            descriptors.append(descriptor)
            parent_descriptor = descriptor
        return descriptors
    except BaseException:
        for descriptor in reversed(descriptors):
            os.close(descriptor)
        raise


def _posix_tree_fact(
    status: os.stat_result,
    *,
    relative_path: str,
) -> RootedTreeNodeFact:
    metadata = snapshot_node_metadata(status)
    return RootedTreeNodeFact(
        relative_path=relative_path,
        identity=metadata.identity,
        kind=RootedTreeNodeKind(metadata.node_kind),
        size=metadata.size,
        link_count=metadata.link_count,
        observation=metadata.observation,
    )


_protocol_check: RootedTreePlatformBackend = PosixRootedTreeBackend()
