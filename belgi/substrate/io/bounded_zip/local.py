"""Local-record binding for central ZIP records."""

from __future__ import annotations

import struct
from typing import NoReturn

from .central import CentralRecord, flags_supported
from .exceptions import BoundedZipError, ZipFailureKind
from .model import BoundedZipEntry, ZipCompression

__all__ = ["bind_local_records"]

_LOCAL_SIGNATURE = 0x04034B50
_DESCRIPTOR_SIGNATURE = 0x08074B50
_ZIP64_END_SIGNATURE = b"PK\x06\x06"
_ZIP64_LOCATOR_SIGNATURE = b"PK\x06\x07"
_UINT32_SENTINEL = 0xFFFFFFFF


def bind_local_records(
    data: bytes,
    *,
    records: tuple[CentralRecord, ...],
    central_offset: int,
) -> tuple[tuple[BoundedZipEntry, ...], bool]:
    entries: dict[int, BoundedZipEntry] = {}
    unsupported = False
    expected_offset = 0
    boundary_known = True
    indexed_records = tuple(enumerate(records))
    usable_records = tuple(
        item for item in indexed_records if item[1].local_offset != _UINT32_SENTINEL
    )
    if len(usable_records) != len(records):
        unsupported = True
    seen_offsets: set[int] = set()
    ordered_records = tuple(
        sorted(
            usable_records,
            key=lambda item: item[1].local_offset,
        )
    )
    for position, (index, central) in enumerate(ordered_records):
        local_offset = central.local_offset
        if local_offset in seen_offsets:
            _malformed_local("ZIP local-header offsets are not unique")
        if boundary_known and local_offset != expected_offset:
            unsupported |= _classify_gap(data[expected_offset:local_offset])
        seen_offsets.add(local_offset)
        if local_offset < 0 or local_offset + 30 > central_offset:
            _malformed_local("ZIP local-header offset is invalid")
        try:
            values = struct.unpack_from("<IHHHHHIIIHH", data, local_offset)
        except struct.error as exc:
            raise BoundedZipError(
                ZipFailureKind.MALFORMED,
                "ZIP local header is truncated",
            ) from exc
        if values[0] != _LOCAL_SIGNATURE:
            _malformed_local("ZIP local-header signature differs")
        needed, flags, method = values[1:4]
        crc32, compressed_size, uncompressed_size = values[6:9]
        name_length, extra_length = values[9:11]
        name_start = local_offset + 30
        data_offset = name_start + name_length + extra_length
        if data_offset > central_offset:
            _malformed_local("ZIP local variable fields overlap the central directory")
        local_name = data[name_start : name_start + name_length]
        uses_data_descriptor = bool(flags & 0x0008)
        if (
            needed != central.needed
            or flags != central.flags
            or method != central.method
            or local_name != central.name
        ):
            _malformed_local("ZIP local and central entry fields differ")
        if not uses_data_descriptor and (
            crc32 != central.crc32
            or compressed_size != central.compressed_size
            or uncompressed_size != central.uncompressed_size
        ):
            _malformed_local("ZIP local and central entry fields differ")
        if (
            extra_length != 0
            or needed != 20
            or uses_data_descriptor
            or not flags_supported(flags=flags, method=method)
        ):
            unsupported = True
        if central.has_zip64_sentinel:
            unsupported = True
            boundary_known = False
            continue
        data_end = data_offset + (
            central.compressed_size if uses_data_descriptor else compressed_size
        )
        next_boundary = (
            ordered_records[position + 1][1].local_offset
            if position + 1 < len(ordered_records)
            else central_offset
        )
        if data_end > next_boundary:
            _malformed_local("ZIP local entry overlaps the following record")
        if central.method in {0, 8}:
            entries[index] = BoundedZipEntry(
                name=central.name,
                creator_system=central.made_by >> 8,
                external_attributes=central.external_attributes,
                flags=central.flags,
                compression=ZipCompression(central.method),
                crc32=central.crc32,
                compressed_size=central.compressed_size,
                uncompressed_size=central.uncompressed_size,
                compressed_data_offset=data_offset,
            )
        else:
            unsupported = True
        if uses_data_descriptor:
            expected_offset = _consume_data_descriptor(
                data,
                start=data_end,
                end=next_boundary,
                central=central,
            )
        else:
            expected_offset = data_end
        boundary_known = True
    if boundary_known and expected_offset != central_offset:
        unsupported |= _classify_gap(data[expected_offset:central_offset])
    if unsupported:
        return (), True
    return tuple(entries[index] for index in range(len(records))), False


def _classify_gap(gap: bytes) -> bool:
    if gap.startswith(_ZIP64_END_SIGNATURE):
        _require_exact_zip64_end_gap(gap)
        return True
    if gap.startswith(_ZIP64_LOCATOR_SIGNATURE):
        if len(gap) != 20:
            _malformed_local("ZIP64 locator framing is malformed")
        return True
    _malformed_local("ZIP local entries are not one exact contiguous layout")


def _require_exact_zip64_end_gap(gap: bytes) -> None:
    if len(gap) < 12:
        _malformed_local("ZIP64 end-record framing is truncated")
    try:
        signature, record_size = struct.unpack_from("<IQ", gap)
    except struct.error as exc:
        raise BoundedZipError(
            ZipFailureKind.MALFORMED,
            "ZIP64 end-record framing is malformed",
        ) from exc
    if signature != 0x06064B50 or record_size < 44:
        _malformed_local("ZIP64 end-record framing is malformed")
    record_end = 12 + record_size
    if record_end == len(gap):
        return
    locator = gap[record_end:]
    if len(locator) != 20 or not locator.startswith(_ZIP64_LOCATOR_SIGNATURE):
        _malformed_local("ZIP64 end-record framing is malformed")


def _consume_data_descriptor(
    data: bytes,
    *,
    start: int,
    end: int,
    central: CentralRecord,
) -> int:
    descriptor = data[start:end]
    values: tuple[int, int, int]
    if len(descriptor) == 12:
        values = struct.unpack("<III", descriptor)
    elif len(descriptor) == 16:
        signature, *fields = struct.unpack("<IIII", descriptor)
        if signature != _DESCRIPTOR_SIGNATURE:
            _malformed_local("ZIP data descriptor signature differs")
        values = tuple(fields)  # type: ignore[assignment]
    elif len(descriptor) == 20:
        values = struct.unpack("<IQQ", descriptor)
    elif len(descriptor) == 24:
        signature, crc32, compressed_size, uncompressed_size = struct.unpack(
            "<IIQQ",
            descriptor,
        )
        if signature != _DESCRIPTOR_SIGNATURE:
            _malformed_local("ZIP data descriptor signature differs")
        values = (crc32, compressed_size, uncompressed_size)
    else:
        _malformed_local("ZIP data descriptor framing is malformed")
    if values != (
        central.crc32,
        central.compressed_size,
        central.uncompressed_size,
    ):
        _malformed_local("ZIP data descriptor and central entry fields differ")
    return end


def _malformed_local(message: str) -> NoReturn:
    raise BoundedZipError(ZipFailureKind.MALFORMED, message)
