"""POSIX filesystem identity, kind, mode, and fingerprint values."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass

from belgi.substrate.io.rooted import FilesystemIdentity, PathFingerprint


@dataclass(frozen=True, slots=True)
class PosixSnapshotNodeMetadata:
    identity: FilesystemIdentity
    node_kind: str
    size: int
    link_count: int
    observation: tuple[object, ...]


def filesystem_identity(status: os.stat_result) -> FilesystemIdentity:
    return status.st_dev, status.st_ino


def is_directory(status: os.stat_result) -> bool:
    return stat.S_ISDIR(status.st_mode)


def is_regular_file(status: os.stat_result) -> bool:
    return stat.S_ISREG(status.st_mode)


def file_mode(status: os.stat_result) -> int:
    return stat.S_IMODE(status.st_mode)


def directory_fingerprint(status: os.stat_result) -> PathFingerprint:
    return (
        status.st_dev,
        status.st_ino,
        status.st_mode,
        status.st_uid,
        status.st_gid,
        getattr(status, "st_flags", 0),
    )


def regular_file_fingerprint(status: os.stat_result) -> PathFingerprint:
    return (
        status.st_dev,
        status.st_ino,
        status.st_mode,
        status.st_size,
        status.st_mtime_ns,
        status.st_ctime_ns,
    )


def snapshot_node_metadata(status: os.stat_result) -> PosixSnapshotNodeMetadata:
    if is_directory(status):
        node_kind = "directory"
        observation: tuple[object, ...] = (
            *directory_fingerprint(status),
            status.st_size,
            status.st_mtime_ns,
            status.st_ctime_ns,
            status.st_nlink,
        )
    elif is_regular_file(status):
        node_kind = "regular-file"
        observation = (*regular_file_fingerprint(status), status.st_nlink)
    else:
        node_kind = "unsupported"
        observation = (
            status.st_dev,
            status.st_ino,
            status.st_mode,
            status.st_size,
            status.st_mtime_ns,
            status.st_ctime_ns,
            status.st_nlink,
            getattr(status, "st_flags", 0),
        )
    return PosixSnapshotNodeMetadata(
        identity=filesystem_identity(status),
        node_kind=node_kind,
        size=status.st_size,
        link_count=status.st_nlink,
        observation=observation,
    )


__all__ = [
    "PosixSnapshotNodeMetadata",
    "directory_fingerprint",
    "file_mode",
    "filesystem_identity",
    "is_directory",
    "is_regular_file",
    "regular_file_fingerprint",
    "snapshot_node_metadata",
]
