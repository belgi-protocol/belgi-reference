"""Deterministic construction of the admitted bounded ZIP subset."""

from __future__ import annotations

import binascii
import struct
import zlib
from collections.abc import Mapping

from .exceptions import BoundedZipError, ZipFailureKind
from .model import BoundedZipLimits, ZipCompression

__all__ = ["encode_bounded_zip"]


def encode_bounded_zip(
    members: Mapping[bytes, bytes],
    *,
    limits: BoundedZipLimits,
    compression: ZipCompression,
) -> bytes:
    if len(members) > limits.entry_count:
        raise BoundedZipError(
            ZipFailureKind.ENTRY_COUNT,
            "ZIP member count exceeds its resource envelope",
        )
    local_records = bytearray()
    central_records: list[bytes] = []
    total_bytes = 0
    for name, value in sorted(members.items()):
        name_bytes = bytes(name)
        member_bytes = bytes(value)
        if len(member_bytes) > limits.member_bytes:
            raise BoundedZipError(
                ZipFailureKind.MEMBER_SIZE,
                "ZIP member exceeds its resource envelope",
            )
        total_bytes += len(member_bytes)
        if total_bytes > limits.total_member_bytes:
            raise BoundedZipError(
                ZipFailureKind.TOTAL_SIZE,
                "ZIP members exceed their total resource envelope",
            )
        if compression is ZipCompression.STORE:
            compressed = member_bytes
        else:
            encoder = zlib.compressobj(level=9, wbits=-15)
            compressed = encoder.compress(member_bytes) + encoder.flush()
        crc32 = binascii.crc32(member_bytes) & 0xFFFFFFFF
        local_offset = len(local_records)
        local_records.extend(
            struct.pack(
                "<IHHHHHIIIHH",
                0x04034B50,
                20,
                0,
                int(compression),
                0,
                0,
                crc32,
                len(compressed),
                len(member_bytes),
                len(name_bytes),
                0,
            )
        )
        local_records.extend(name_bytes)
        local_records.extend(compressed)
        central_records.append(
            struct.pack(
                "<IHHHHHHIIIHHHHHII",
                0x02014B50,
                0x0314,
                20,
                0,
                int(compression),
                0,
                0,
                crc32,
                len(compressed),
                len(member_bytes),
                len(name_bytes),
                0,
                0,
                0,
                0,
                0x81A40000,
                local_offset,
            )
            + name_bytes
        )
    central_offset = len(local_records)
    central = b"".join(central_records)
    archive = (
        bytes(local_records)
        + central
        + struct.pack(
            "<IHHHHIIH",
            0x06054B50,
            0,
            0,
            len(members),
            len(members),
            len(central),
            central_offset,
            0,
        )
    )
    if len(archive) > limits.archive_bytes:
        raise BoundedZipError(
            ZipFailureKind.OUTER_SIZE,
            "encoded ZIP exceeds its outer byte envelope",
        )
    return archive
