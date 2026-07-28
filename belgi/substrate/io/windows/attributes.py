"""File-attribute mutation for Windows filesystem handles."""

from __future__ import annotations

import ctypes

from .abi import (
    FILE_ATTRIBUTE_NORMAL,
    FILE_ATTRIBUTE_READONLY,
    NT_FILE_BASIC_INFORMATION_CLASS,
    CHandle,
    FileBasicInfo,
    IoStatusBlock,
    Ntdll,
    nt_success,
    raise_ntstatus,
)
from .file_info import query_info
from .handle import WindowsHandle


def set_readonly(handle: WindowsHandle, readonly: bool) -> None:
    current = query_info(handle)
    attributes = current.attributes
    attributes = (
        attributes | FILE_ATTRIBUTE_READONLY
        if readonly
        else attributes & ~FILE_ATTRIBUTE_READONLY
    )
    if attributes == current.attributes:
        return
    if attributes == 0:
        attributes = FILE_ATTRIBUTE_NORMAL
    basic = FileBasicInfo(0, 0, 0, 0, attributes)
    io_status = IoStatusBlock()
    status = int(
        Ntdll.NtSetInformationFile(
            CHandle(handle.value),
            ctypes.byref(io_status),
            ctypes.byref(basic),
            ctypes.sizeof(basic),
            NT_FILE_BASIC_INFORMATION_CLASS,
        )
    )
    if not nt_success(status):
        raise_ntstatus(status)
    if query_info(handle).is_readonly != readonly:
        raise OSError("Windows readonly attribute did not apply")


__all__ = ["set_readonly"]
