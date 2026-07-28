"""Central-directory framing for the admitted bounded ZIP subset."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import NoReturn

from .exceptions import BoundedZipError, ZipFailureKind

__all__ = ["CentralRecord", "flags_supported", "parse_central_records"]

_CENTRAL_SIGNATURE = 0x02014B50
_CENTRAL_DIGITAL_SIGNATURE = 0x05054B50
_CENTRAL_FIXED_BYTES = 46
_UINT16_SENTINEL = 0xFFFF
_UINT32_SENTINEL = 0xFFFFFFFF
_MAXIMUM_CLASSIC_RECORDS = _UINT16_SENTINEL


@dataclass(frozen=True, slots=True, kw_only=True)
class CentralRecord:
    name: bytes
    made_by: int
    needed: int
    flags: int
    method: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    external_attributes: int
    local_offset: int

    @property
    def has_zip64_sentinel(self) -> bool:
        return any(
            value == _UINT32_SENTINEL
            for value in (
                self.compressed_size,
                self.uncompressed_size,
                self.local_offset,
            )
        )


def parse_central_records(
    data: bytes,
    *,
    central_offset: int,
    central_size: int,
    total_entries: int,
) -> tuple[tuple[CentralRecord, ...], bool, bool]:
    offset = central_offset
    central_end = central_offset + central_size
    if (
        central_offset < 0
        or central_size < 0
        or central_end > len(data)
        or central_size < total_entries * _CENTRAL_FIXED_BYTES
    ):
        _malformed_central("ZIP central-directory bounds are inconsistent")
    records: list[CentralRecord] = []
    unsupported = False
    records_materialized = total_entries <= _MAXIMUM_CLASSIC_RECORDS
    # Stage 2 framing precedes the Stage 3 entry-count result. The enclosing
    # archive-size check bounds this complete scan. ZIP64 counts above the
    # classic format cap are scanned without retaining amplified Python objects.
    for _ in range(total_entries):
        if offset + _CENTRAL_FIXED_BYTES > central_end:
            _malformed_central("ZIP central-directory entry is truncated")
        try:
            values = struct.unpack_from("<IHHHHHHIIIHHHHHII", data, offset)
        except struct.error as exc:
            raise BoundedZipError(
                ZipFailureKind.MALFORMED,
                "ZIP central-directory entry is malformed",
            ) from exc
        if values[0] != _CENTRAL_SIGNATURE:
            _malformed_central("ZIP central-directory signature differs")
        made_by, needed, flags, method = values[1:5]
        crc32, compressed_size, uncompressed_size = values[7:10]
        name_length, extra_length, comment_length = values[10:13]
        disk_start, external_attributes, local_offset = (
            values[13],
            values[15],
            values[16],
        )
        entry_end = (
            offset + _CENTRAL_FIXED_BYTES + name_length + extra_length + comment_length
        )
        if entry_end > central_end:
            _malformed_central("ZIP central-directory variable fields are truncated")
        record = CentralRecord(
            name=data[
                offset + _CENTRAL_FIXED_BYTES : offset
                + _CENTRAL_FIXED_BYTES
                + name_length
            ],
            made_by=made_by,
            needed=needed,
            flags=flags,
            method=method,
            crc32=crc32,
            compressed_size=compressed_size,
            uncompressed_size=uncompressed_size,
            external_attributes=external_attributes,
            local_offset=local_offset,
        )
        if (
            record.has_zip64_sentinel
            or disk_start == _UINT16_SENTINEL
            or needed != 20
            or made_by & 0xFF != 20
            or disk_start != 0
            or extra_length != 0
            or comment_length != 0
            or not flags_supported(flags=flags, method=method)
        ):
            unsupported = True
        if records_materialized:
            records.append(record)
        offset = entry_end
    if offset != central_end:
        unsupported |= _consume_central_digital_signature(
            data,
            offset=offset,
            central_end=central_end,
        )
    return tuple(records), unsupported, records_materialized


def _consume_central_digital_signature(
    data: bytes,
    *,
    offset: int,
    central_end: int,
) -> bool:
    if offset + 6 > central_end:
        _malformed_central("ZIP central-directory size does not match its entries")
    try:
        signature, payload_size = struct.unpack_from("<IH", data, offset)
    except struct.error as exc:
        raise BoundedZipError(
            ZipFailureKind.MALFORMED,
            "ZIP central-directory digital signature is truncated",
        ) from exc
    if signature != _CENTRAL_DIGITAL_SIGNATURE:
        _malformed_central("ZIP central-directory size does not match its entries")
    if offset + 6 + payload_size != central_end:
        _malformed_central("ZIP central-directory digital signature is malformed")
    return True


def flags_supported(*, flags: int, method: int) -> bool:
    if method == 0:
        return flags in {0x0000, 0x0800}
    if method == 8:
        return flags & ~0x0806 == 0
    return False


def _malformed_central(message: str) -> NoReturn:
    raise BoundedZipError(ZipFailureKind.MALFORMED, message)
