"""Complete bounded reading over one platform-owned rooted-tree observer."""

from __future__ import annotations

from pathlib import Path
from typing import NoReturn

from belgi.substrate.io.access import lexical_absolute_path
from belgi.substrate.io.exceptions import (
    RootedPathSymlinkError,
    WindowsReparsePointError,
)

from .exceptions import RootedTreeError
from .model import (
    RootedTreeDirectoryDescendantPredicate,
    RootedTreeEntry,
    RootedTreeEntryValidator,
    RootedTreeFailureKind,
    RootedTreeLimits,
    RootedTreeNodeFact,
    RootedTreeNodeKind,
    RootedTreePlatformBackend,
    RootedTreePlatformSession,
    RootedTreeSnapshot,
)

__all__ = ["read_tree_snapshot_with_backend"]

_READ_CHUNK_BYTES = 65_536


def read_tree_snapshot_with_backend(
    root: Path,
    *,
    limits: RootedTreeLimits,
    backend: RootedTreePlatformBackend,
    entry_validator: RootedTreeEntryValidator | None = None,
    directory_descendant_predicate: (
        RootedTreeDirectoryDescendantPredicate | None
    ) = None,
) -> RootedTreeSnapshot:
    absolute_root = lexical_absolute_path(root)
    session_established = False
    try:
        with backend.open_session(absolute_root) as session:
            session_established = True
            root_fact = session.root_fact()
            if root_fact.kind is not RootedTreeNodeKind.DIRECTORY:
                _unsupported("root must be one real directory")
            return _read_stable_tree(
                root_fact=root_fact,
                limits=limits,
                session=session,
                entry_validator=entry_validator,
                directory_descendant_predicate=directory_descendant_predicate,
            )
    except RootedTreeError:
        raise
    except (RootedPathSymlinkError, WindowsReparsePointError) as exc:
        if not session_established:
            raise RootedTreeError(
                RootedTreeFailureKind.UNSUPPORTED_ENTRY_TYPE,
                "root and every absolute ancestor must be real directories",
            ) from exc
        _mutated("root ancestry changed during bounded reading", cause=exc)
    except (OSError, ValueError) as exc:
        message = (
            "root could not be authenticated"
            if not session_established
            else "rooted tree changed during bounded reading"
        )
        _mutated(message, cause=exc)


def _read_stable_tree(
    *,
    root_fact: RootedTreeNodeFact,
    limits: RootedTreeLimits,
    session: RootedTreePlatformSession,
    entry_validator: RootedTreeEntryValidator | None,
    directory_descendant_predicate: (RootedTreeDirectoryDescendantPredicate | None),
) -> RootedTreeSnapshot:
    facts, path_resource_exceeded = _enumerate_tree(
        limits=limits,
        session=session,
        directory_descendant_predicate=directory_descendant_predicate,
    )
    if path_resource_exceeded:
        raise RootedTreeError(
            RootedTreeFailureKind.INVALID_ENTRY_NAME,
            "rooted directory exceeds its traversal path envelope",
        )
    if entry_validator is not None:
        entry_validator(facts)
    _require_supported_facts(facts)
    files = tuple(
        fact for fact in facts if fact.kind is RootedTreeNodeKind.REGULAR_FILE
    )
    _require_byte_limits(files=files, limits=limits)
    entries = _read_files(session=session, files=files, limits=limits)
    try:
        final_root_fact = session.root_fact()
        final_facts, final_path_resource_exceeded = _enumerate_tree(
            limits=limits,
            session=session,
            directory_descendant_predicate=directory_descendant_predicate,
        )
    except RootedTreeError as exc:
        _mutated("rooted tree changed before final observation", cause=exc)
    if (
        final_root_fact != root_fact
        or final_facts != facts
        or final_path_resource_exceeded
    ):
        _mutated("rooted tree changed during bounded reading")
    return RootedTreeSnapshot(entries=entries)


def _enumerate_tree(
    *,
    limits: RootedTreeLimits,
    session: RootedTreePlatformSession,
    directory_descendant_predicate: (RootedTreeDirectoryDescendantPredicate | None),
) -> tuple[tuple[RootedTreeNodeFact, ...], bool]:
    facts: list[RootedTreeNodeFact] = []
    pending: list[tuple[str, ...]] = [()]
    directory_entry_limit = limits.directory_entry_count
    candidate_member_count = 0
    path_resource_exceeded = False
    while pending:
        relative_directory = pending.pop()
        child_directories: list[tuple[str, ...]] = []
        remaining_entries = directory_entry_limit - len(facts)
        for fact in session.directory_entries(
            relative_directory=relative_directory,
            maximum_entries=remaining_entries,
            maximum_candidate_members=(limits.member_count - candidate_member_count),
        ):
            facts.append(fact)
            if len(facts) > directory_entry_limit:
                raise RootedTreeError(
                    RootedTreeFailureKind.DIRECTORY_ENTRY_COUNT,
                    "rooted tree exceeds its directory-entry-count envelope",
                )
            if fact.kind is RootedTreeNodeKind.DIRECTORY:
                if _traversable_path_resources_exceeded(fact, limits=limits):
                    path_resource_exceeded = True
                    continue
                if (
                    directory_descendant_predicate is not None
                    and not directory_descendant_predicate(fact)
                ):
                    continue
                child_directories.append(tuple(fact.relative_path.split("/")))
                continue
            candidate_member_count += 1
            if candidate_member_count > limits.member_count:
                raise RootedTreeError(
                    RootedTreeFailureKind.MEMBER_COUNT,
                    "rooted tree exceeds its member-count envelope",
                )
        pending.extend(reversed(child_directories))
    return tuple(facts), path_resource_exceeded


def _require_supported_facts(facts: tuple[RootedTreeNodeFact, ...]) -> None:
    paths_with_file_descendants: set[str] = set()
    for fact in facts:
        if fact.kind is not RootedTreeNodeKind.REGULAR_FILE:
            continue
        components = fact.relative_path.split("/")
        paths_with_file_descendants.update(
            "/".join(components[:component_count])
            for component_count in range(1, len(components))
        )
    for fact in facts:
        if fact.kind is RootedTreeNodeKind.DIRECTORY:
            if fact.relative_path not in paths_with_file_descendants:
                _unsupported(f"directory is empty or unneeded: {fact.relative_path}")
            continue
        if fact.kind is not RootedTreeNodeKind.REGULAR_FILE or fact.link_count != 1:
            _unsupported(
                f"entry is not a single-link regular file: {fact.relative_path}"
            )


def _traversable_path_resources_exceeded(
    fact: RootedTreeNodeFact,
    *,
    limits: RootedTreeLimits,
) -> bool:
    segments = fact.relative_path.split("/")
    encoded_segments = tuple(
        segment.encode("utf-8", errors="surrogatepass") for segment in segments
    )
    encoded_path = fact.relative_path.encode("utf-8", errors="surrogatepass")
    return (
        len(segments) > limits.path_segments
        or len(encoded_path) > limits.path_bytes
        or any(len(segment) > limits.path_segment_bytes for segment in encoded_segments)
    )


def _require_byte_limits(
    *,
    files: tuple[RootedTreeNodeFact, ...],
    limits: RootedTreeLimits,
) -> None:
    oversized = next(
        (fact for fact in files if fact.size > limits.member_bytes),
        None,
    )
    if oversized is not None:
        raise RootedTreeError(
            RootedTreeFailureKind.MEMBER_SIZE,
            f"rooted file exceeds its byte envelope: {oversized.relative_path}",
        )
    if sum(fact.size for fact in files) > limits.total_member_bytes:
        raise RootedTreeError(
            RootedTreeFailureKind.TOTAL_SIZE,
            "rooted tree exceeds its total byte envelope",
        )


def _read_files(
    *,
    session: RootedTreePlatformSession,
    files: tuple[RootedTreeNodeFact, ...],
    limits: RootedTreeLimits,
) -> tuple[RootedTreeEntry, ...]:
    entries: list[RootedTreeEntry] = []
    total_bytes = 0
    for fact in files:
        with session.open_binary_file(
            relative_path=tuple(fact.relative_path.split("/"))
        ) as (stream, identity):
            if identity != fact.identity:
                _mutated(f"file identity changed: {fact.relative_path}")
            content = bytearray()
            while True:
                chunk = stream.read(
                    min(_READ_CHUNK_BYTES, limits.member_bytes - len(content) + 1)
                )
                if not chunk:
                    break
                content.extend(chunk)
                if len(content) > limits.member_bytes:
                    raise RootedTreeError(
                        RootedTreeFailureKind.MEMBER_SIZE,
                        f"rooted file exceeds its byte envelope: {fact.relative_path}",
                    )
            if len(content) != fact.size:
                _mutated(f"file size changed: {fact.relative_path}")
        total_bytes += len(content)
        if total_bytes > limits.total_member_bytes:
            raise RootedTreeError(
                RootedTreeFailureKind.TOTAL_SIZE,
                "rooted tree exceeds its total byte envelope",
            )
        entries.append(
            RootedTreeEntry(relative_path=fact.relative_path, octets=bytes(content))
        )
    return tuple(entries)


def _unsupported(message: str) -> NoReturn:
    raise RootedTreeError(RootedTreeFailureKind.UNSUPPORTED_ENTRY_TYPE, message)


def _mutated(message: str, *, cause: BaseException | None = None) -> NoReturn:
    error = RootedTreeError(RootedTreeFailureKind.MUTATED, message)
    if cause is None:
        raise error
    raise error from cause
