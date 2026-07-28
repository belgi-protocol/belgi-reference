"""Bounded direct reading of inspected ZIP member streams."""

from __future__ import annotations

import binascii
import zlib

from .exceptions import BoundedZipError, ZipFailureKind
from .model import (
    BoundedZipArchive,
    BoundedZipEntry,
    BoundedZipLimits,
    BoundedZipReadResult,
    ZipCompression,
)
from .output import BoundedZipOutputCounters, admit_bounded_zip_output

__all__ = ["read_bounded_zip_entry"]

_STREAM_INPUT_CHUNK_BYTES = 64 * 1024


def read_bounded_zip_entry(
    archive: BoundedZipArchive,
    entry: BoundedZipEntry,
    *,
    limits: BoundedZipLimits,
    total_bytes_before: int,
) -> BoundedZipReadResult:
    start = entry.compressed_data_offset
    end = start + entry.compressed_size
    compressed = memoryview(archive.archive_bytes)[start:end]
    maximum = min(
        limits.member_bytes,
        limits.total_member_bytes - total_bytes_before,
    )
    try:
        if entry.compression is ZipCompression.STORE:
            output = _bounded_store(compressed, maximum=maximum)
        else:
            output = _bounded_deflate(compressed, maximum=maximum)
    except zlib.error as exc:
        raise BoundedZipError(
            ZipFailureKind.STREAM_MISMATCH,
            "ZIP DEFLATE stream is invalid",
        ) from exc
    admission = admit_bounded_zip_output(
        counters=BoundedZipOutputCounters(
            member_bytes=0,
            total_bytes=total_bytes_before,
        ),
        produced_bytes=len(output),
        limits=limits,
    )
    if admission.failure_kind is not None:
        raise BoundedZipError(
            admission.failure_kind,
            "ZIP member exceeds an actual-output byte envelope",
        )
    if (
        len(output) != entry.uncompressed_size
        or binascii.crc32(output) & 0xFFFFFFFF != entry.crc32
    ):
        raise BoundedZipError(
            ZipFailureKind.STREAM_MISMATCH,
            "ZIP member length or CRC-32 differs from its declaration",
        )
    return BoundedZipReadResult(
        octets=output,
        member_bytes=admission.counters.member_bytes,
        total_bytes=admission.counters.total_bytes,
    )


def _bounded_store(compressed: memoryview, *, maximum: int) -> bytes:
    output = bytearray()
    cursor = 0
    while cursor < len(compressed) and len(output) <= maximum:
        probe_remaining = maximum + 1 - len(output)
        next_cursor = min(
            len(compressed),
            cursor + min(_STREAM_INPUT_CHUNK_BYTES, probe_remaining),
        )
        output.extend(compressed[cursor:next_cursor])
        cursor = next_cursor
    return bytes(output)


def _bounded_deflate(compressed: memoryview, *, maximum: int) -> bytes:
    decoder = zlib.decompressobj(wbits=-15)
    output = bytearray()
    input_cursor = 0
    while True:
        if decoder.unconsumed_tail:
            pending: bytes | memoryview = decoder.unconsumed_tail
        elif input_cursor < len(compressed):
            next_cursor = min(
                len(compressed),
                input_cursor + _STREAM_INPUT_CHUNK_BYTES,
            )
            pending = compressed[input_cursor:next_cursor]
            input_cursor = next_cursor
        else:
            pending = b""
        probe_octets = maximum + 1 - len(output)
        chunk = decoder.decompress(pending, max(1, probe_octets))
        output.extend(chunk)
        if len(output) > maximum:
            return bytes(output)
        if decoder.eof:
            break
        if (
            input_cursor == len(compressed)
            and not decoder.unconsumed_tail
            and not chunk
        ):
            break
    if (
        not decoder.eof
        or decoder.unused_data
        or decoder.unconsumed_tail
        or input_cursor != len(compressed)
    ):
        raise BoundedZipError(
            ZipFailureKind.STREAM_MISMATCH,
            "ZIP DEFLATE stream boundary differs from its declaration",
        )
    return bytes(output)
