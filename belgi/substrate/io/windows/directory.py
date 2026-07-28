"""Stable native enumeration of one Windows directory handle."""

from __future__ import annotations

import ctypes
from collections.abc import Iterator

from .abi import (
    NT_FILE_NAMES_INFORMATION_CLASS,
    STATUS_BUFFER_OVERFLOW,
    STATUS_NO_MORE_FILES,
    CHandle,
    IoStatusBlock,
    Ntdll,
    nt_success,
    raise_ntstatus,
    unsigned_status,
)
from .file_info import require_case_insensitive_directory
from .handle import WindowsHandle
from .path_open import validate_component


def iter_directory(handle: WindowsHandle) -> Iterator[str]:
    require_case_insensitive_directory(handle)
    seen_names: set[str] = set()
    restart = True
    while True:
        buffer = ctypes.create_string_buffer(64 * 1024)
        io_status = IoStatusBlock()
        status = int(
            Ntdll.NtQueryDirectoryFile(
                CHandle(handle.value),
                None,
                None,
                None,
                ctypes.byref(io_status),
                buffer,
                len(buffer),
                NT_FILE_NAMES_INFORMATION_CLASS,
                0,
                None,
                1 if restart else 0,
            )
        )
        unsigned = unsigned_status(status)
        if unsigned == STATUS_NO_MORE_FILES:
            break
        if not nt_success(status) and unsigned != STATUS_BUFFER_OVERFLOW:
            raise_ntstatus(status)
        written = int(io_status.Information)
        if written <= 0 or written > len(buffer):
            raise OSError("Windows directory enumeration made no progress")
        for name in _iter_names(buffer, written):
            folded_name = name.casefold()
            if folded_name in seen_names:
                raise OSError("Windows directory enumeration returned ambiguous names")
            seen_names.add(folded_name)
            yield name
        restart = False


def enumerate_directory(handle: WindowsHandle) -> tuple[str, ...]:
    return tuple(
        sorted(iter_directory(handle), key=lambda item: (item.casefold(), item))
    )


def _iter_names(
    buffer: ctypes.Array[ctypes.c_char],
    written: int,
) -> Iterator[str]:
    offset = 0
    base = ctypes.addressof(buffer)
    while offset < written:
        if offset + 12 > written:
            raise OSError("malformed Windows directory enumeration entry")
        next_offset = int.from_bytes(ctypes.string_at(base + offset, 4), "little")
        name_length = int.from_bytes(ctypes.string_at(base + offset + 8, 4), "little")
        name_end = offset + 12 + name_length
        if name_length % 2 or name_end > written:
            raise OSError("malformed Windows directory enumeration name")
        name = ctypes.string_at(base + offset + 12, name_length).decode("utf-16-le")
        if name not in {".", ".."}:
            validate_component(name)
            yield name
        if next_offset == 0:
            break
        if next_offset < 12 or offset + next_offset > written:
            raise OSError("malformed Windows directory enumeration offset")
        offset += next_offset


__all__ = ["enumerate_directory", "iter_directory"]
