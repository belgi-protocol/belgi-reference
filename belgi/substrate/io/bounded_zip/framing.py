"""Strict structural inspection of bounded ZIP archives."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import NoReturn

from .central import parse_central_records
from .exceptions import BoundedZipError, ZipFailureKind
from .local import bind_local_records
from .model import BoundedZipArchive, BoundedZipLimits

__all__ = ["inspect_bounded_zip"]

_EOCD_SIGNATURE = b"PK\x05\x06"
_ZIP64_END_SIGNATURE = 0x06064B50
_ZIP64_LOCATOR_SIGNATURE = 0x07064B50
_UINT16_SENTINEL = 0xFFFF
_UINT32_SENTINEL = 0xFFFFFFFF


@dataclass(frozen=True, slots=True, kw_only=True)
class _EndRecord:
    central_offset: int
    central_size: int
    total_entries: int
    eocd_offset: int


@dataclass(frozen=True, slots=True, kw_only=True)
class _Zip64EndRecord:
    central_offset: int
    central_size: int
    disk_entries: int
    total_entries: int
    record_offset: int
    split_disk: bool


def inspect_bounded_zip(
    archive_bytes: bytes,
    *,
    limits: BoundedZipLimits,
) -> BoundedZipArchive:
    data = bytes(archive_bytes)
    if len(data) > limits.archive_bytes:
        raise BoundedZipError(
            ZipFailureKind.OUTER_SIZE,
            "ZIP archive exceeds its outer byte envelope",
        )
    end, end_unsupported = _parse_eocd(data)
    records, central_unsupported, records_materialized = parse_central_records(
        data,
        central_offset=end.central_offset,
        central_size=end.central_size,
        total_entries=end.total_entries,
    )
    if not records_materialized:
        raise BoundedZipError(
            ZipFailureKind.UNSUPPORTED_FEATURE,
            "ZIP64 entry counts are outside the admitted subset",
        )
    entries, local_unsupported = bind_local_records(
        data,
        records=records,
        central_offset=end.central_offset,
    )
    if end_unsupported or central_unsupported or local_unsupported:
        raise BoundedZipError(
            ZipFailureKind.UNSUPPORTED_FEATURE,
            "ZIP archive uses a feature outside the admitted subset",
        )
    if end.total_entries > limits.entry_count:
        raise BoundedZipError(
            ZipFailureKind.ENTRY_COUNT,
            "ZIP archive exceeds its entry-count envelope",
        )
    return BoundedZipArchive(archive_bytes=data, entries=entries)


def _parse_eocd(data: bytes) -> tuple[_EndRecord, bool]:
    offset = _find_eocd_offset(data)
    try:
        (
            signature,
            disk,
            central_disk,
            disk_entries,
            total_entries,
            central_size,
            central_offset,
            comment_length,
        ) = struct.unpack_from("<IHHHHIIH", data, offset)
    except struct.error as exc:
        raise BoundedZipError(
            ZipFailureKind.MALFORMED,
            "ZIP EOCD is truncated",
        ) from exc
    if offset + 22 + comment_length != len(data):
        _malformed_framing("ZIP archive contains trailing bytes or a malformed comment")
    if signature != 0x06054B50:
        _malformed_framing("ZIP EOCD signature differs")
    split_disk = disk != 0 or central_disk != 0 or disk_entries != total_entries
    has_sentinel = any(
        value == sentinel
        for value, sentinel in (
            (disk_entries, _UINT16_SENTINEL),
            (total_entries, _UINT16_SENTINEL),
            (central_size, _UINT32_SENTINEL),
            (central_offset, _UINT32_SENTINEL),
        )
    )
    zip64 = _zip64_end_record(data, eocd_offset=offset)
    if zip64 is not None:
        _require_matching_non_sentinel(
            disk_entries=disk_entries,
            total_entries=total_entries,
            central_size=central_size,
            central_offset=central_offset,
            zip64=zip64,
        )
        if zip64.central_offset + zip64.central_size != zip64.record_offset:
            _malformed_framing("ZIP64 central-directory layout is inconsistent")
        return (
            _EndRecord(
                central_offset=zip64.central_offset,
                central_size=zip64.central_size,
                total_entries=zip64.total_entries,
                eocd_offset=offset,
            ),
            True,
        )
    if central_offset + central_size != offset:
        _malformed_framing("ZIP central-directory layout is inconsistent")
    return (
        _EndRecord(
            central_offset=central_offset,
            central_size=central_size,
            total_entries=total_entries,
            eocd_offset=offset,
        ),
        split_disk or comment_length != 0 or has_sentinel,
    )


def _find_eocd_offset(data: bytes) -> int:
    minimum = max(0, len(data) - 22 - _UINT16_SENTINEL)
    for offset in range(len(data) - 22, minimum - 1, -1):
        if data[offset : offset + 4] != _EOCD_SIGNATURE:
            continue
        try:
            comment_length = struct.unpack_from("<H", data, offset + 20)[0]
        except struct.error:
            continue
        if offset + 22 + comment_length == len(data):
            return offset
    _malformed_framing("ZIP EOCD is malformed")


def _zip64_end_record(
    data: bytes,
    *,
    eocd_offset: int,
) -> _Zip64EndRecord | None:
    locator_offset = eocd_offset - 20
    if locator_offset < 0:
        return None
    try:
        locator_signature, locator_disk, record_offset, total_disks = (
            struct.unpack_from("<IIQI", data, locator_offset)
        )
    except struct.error:
        return None
    if locator_signature != _ZIP64_LOCATOR_SIGNATURE:
        return None
    if record_offset + 12 > locator_offset:
        _malformed_framing("ZIP64 end record offset is invalid")
    try:
        record_signature, record_size = struct.unpack_from("<IQ", data, record_offset)
    except struct.error as exc:
        raise BoundedZipError(
            ZipFailureKind.MALFORMED,
            "ZIP64 end record is truncated",
        ) from exc
    if record_signature != _ZIP64_END_SIGNATURE or record_size < 44:
        _malformed_framing("ZIP64 end record is malformed")
    if record_offset + 12 + record_size != locator_offset:
        _malformed_framing("ZIP64 end record size is inconsistent")
    try:
        (
            _made_by,
            _needed,
            disk,
            central_disk,
            disk_entries,
            total_entries,
            central_size,
            central_offset,
        ) = struct.unpack_from("<HHIIQQQQ", data, record_offset + 12)
    except struct.error as exc:
        raise BoundedZipError(
            ZipFailureKind.MALFORMED,
            "ZIP64 end record fields are truncated",
        ) from exc
    if total_disks == 0:
        _malformed_framing("ZIP64 locator declares no disks")
    return _Zip64EndRecord(
        central_offset=central_offset,
        central_size=central_size,
        disk_entries=disk_entries,
        total_entries=total_entries,
        record_offset=record_offset,
        split_disk=(
            locator_disk != 0
            or total_disks != 1
            or disk != 0
            or central_disk != 0
            or disk_entries != total_entries
        ),
    )


def _require_matching_non_sentinel(
    *,
    disk_entries: int,
    total_entries: int,
    central_size: int,
    central_offset: int,
    zip64: _Zip64EndRecord,
) -> None:
    pairs = (
        (disk_entries, _UINT16_SENTINEL, zip64.disk_entries),
        (total_entries, _UINT16_SENTINEL, zip64.total_entries),
        (central_size, _UINT32_SENTINEL, zip64.central_size),
        (central_offset, _UINT32_SENTINEL, zip64.central_offset),
    )
    if any(
        value != sentinel and value != expanded for value, sentinel, expanded in pairs
    ):
        _malformed_framing("ZIP64 and EOCD fields differ")


def _malformed_framing(message: str) -> NoReturn:
    raise BoundedZipError(ZipFailureKind.MALFORMED, message)
