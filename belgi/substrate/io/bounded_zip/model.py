"""Platform-neutral values for the bounded ZIP mechanism."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

__all__ = [
    "BoundedZipArchive",
    "BoundedZipEntry",
    "BoundedZipLimits",
    "BoundedZipReadResult",
    "ZipCompression",
]


class ZipCompression(IntEnum):
    STORE = 0
    DEFLATE = 8


@dataclass(frozen=True, slots=True, kw_only=True)
class BoundedZipLimits:
    archive_bytes: int
    entry_count: int
    member_bytes: int
    total_member_bytes: int


@dataclass(frozen=True, slots=True, kw_only=True)
class BoundedZipEntry:
    name: bytes
    creator_system: int
    external_attributes: int
    flags: int
    compression: ZipCompression
    crc32: int
    compressed_size: int
    uncompressed_size: int
    compressed_data_offset: int


@dataclass(frozen=True, slots=True, kw_only=True)
class BoundedZipArchive:
    archive_bytes: bytes
    entries: tuple[BoundedZipEntry, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class BoundedZipReadResult:
    octets: bytes
    member_bytes: int
    total_bytes: int
