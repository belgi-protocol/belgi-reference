"""CRT stream ownership and durable flush for Windows filesystem handles."""

from __future__ import annotations

import os
from typing import Any, BinaryIO

from .abi import CHandle, Kernel32, raise_last_error
from .file_info import WindowsFileInfo, query_info
from .handle import WindowsHandle

try:
    import msvcrt
except ImportError:  # pragma: no cover - non-Windows import/typecheck seam
    msvcrt = None  # type: ignore[assignment]

Msvcrt: Any = msvcrt


def query_info_for_file_descriptor(descriptor: int) -> WindowsFileInfo:
    raw = _os_handle(descriptor)
    borrowed = WindowsHandle(raw)
    try:
        return query_info(borrowed)
    finally:
        borrowed.detach()


def binary_stream(handle: WindowsHandle, *, writable: bool = False) -> BinaryIO:
    if Msvcrt is None:
        raise OSError("Windows CRT handles require Windows")
    flags = 0x8000 | 0x0080 | (0x0001 if writable else 0)
    descriptor = int(Msvcrt.open_osfhandle(handle.value, flags))
    if descriptor == -1:
        raise OSError("Windows CRT file descriptor allocation failed")
    handle.detach()
    try:
        return open(descriptor, "wb" if writable else "rb", closefd=True)
    except BaseException:
        os.close(descriptor)
        raise


def flush_file_descriptor(descriptor: int) -> None:
    if not Kernel32.FlushFileBuffers(CHandle(_os_handle(descriptor))):
        raise_last_error()


def _os_handle(descriptor: int) -> int:
    if Msvcrt is None:
        raise OSError("Windows CRT handles require Windows")
    raw = int(Msvcrt.get_osfhandle(descriptor))
    if raw == -1:
        raise OSError("invalid Windows CRT file descriptor")
    return raw


__all__ = [
    "binary_stream",
    "flush_file_descriptor",
    "query_info_for_file_descriptor",
]
