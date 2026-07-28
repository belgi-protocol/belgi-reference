"""Metadata query and entry classification for Windows handles."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
from typing import Any

from belgi.substrate.io.exceptions import WindowsReparsePointError

from .abi import (
    FILE_ATTRIBUTE_REPARSE_POINT,
    FILE_ATTRIBUTE_TAG_INFORMATION_CLASS,
    FILE_BASIC_INFORMATION_CLASS,
    FILE_CASE_SENSITIVE_INFORMATION_CLASS,
    FILE_CS_FLAG_CASE_SENSITIVE_DIR,
    FILE_ID_INFORMATION_CLASS,
    FILE_STANDARD_INFORMATION_CLASS,
    CHandle,
    FileAttributeTagInfo,
    FileBasicInfo,
    FileCaseSensitiveInfo,
    FileIdInfo,
    FileStandardInfo,
    Kernel32,
    raise_last_error,
)
from .access import WindowsEntryKind
from .handle import WindowsHandle


@dataclass(frozen=True, slots=True)
class WindowsFileInfo:
    volume_serial_number: int
    file_id: bytes
    attributes: int
    reparse_tag: int
    creation_time: int
    last_access_time: int
    last_write_time: int
    change_time: int
    allocation_size: int
    end_of_file: int
    number_of_links: int
    delete_pending: bool
    is_directory: bool

    @property
    def identity(self) -> tuple[int, int]:
        return self.volume_serial_number, int.from_bytes(self.file_id, "little")

    @property
    def is_reparse_point(self) -> bool:
        return bool(self.attributes & FILE_ATTRIBUTE_REPARSE_POINT)

    @property
    def is_regular_file(self) -> bool:
        return not self.is_directory and not self.is_reparse_point

    @property
    def is_readonly(self) -> bool:
        return bool(self.attributes & 0x00000001)


def query_info(handle: WindowsHandle) -> WindowsFileInfo:
    file_id = _query_handle_info(handle, FILE_ID_INFORMATION_CLASS, FileIdInfo)
    tag = _query_handle_info(
        handle,
        FILE_ATTRIBUTE_TAG_INFORMATION_CLASS,
        FileAttributeTagInfo,
    )
    basic = _query_handle_info(handle, FILE_BASIC_INFORMATION_CLASS, FileBasicInfo)
    standard = _query_handle_info(
        handle,
        FILE_STANDARD_INFORMATION_CLASS,
        FileStandardInfo,
    )
    if int(tag.FileAttributes) != int(basic.FileAttributes):
        raise OSError("Windows file attributes changed during handle inspection")
    return WindowsFileInfo(
        int(file_id.VolumeSerialNumber),
        bytes(file_id.FileId.Identifier),
        int(tag.FileAttributes),
        int(tag.ReparseTag),
        int(basic.CreationTime),
        int(basic.LastAccessTime),
        int(basic.LastWriteTime),
        int(basic.ChangeTime),
        int(standard.AllocationSize),
        int(standard.EndOfFile),
        int(standard.NumberOfLinks),
        bool(standard.DeletePending),
        bool(standard.Directory),
    )


def require_opened_kind(
    handle: WindowsHandle,
    kind: WindowsEntryKind,
    *,
    reject_reparse: bool = True,
) -> None:
    info = query_info(handle)
    require_file_info_kind(info, kind, reject_reparse=reject_reparse)


def require_file_info_kind(
    info: WindowsFileInfo,
    kind: WindowsEntryKind,
    *,
    reject_reparse: bool = True,
) -> WindowsFileInfo:
    if reject_reparse and info.is_reparse_point:
        raise WindowsReparsePointError("Windows reparse point not allowed")
    if info.delete_pending:
        raise ValueError("Windows path is pending deletion")
    if kind is WindowsEntryKind.DIRECTORY and not info.is_directory:
        raise NotADirectoryError("expected a Windows directory")
    if kind is WindowsEntryKind.REGULAR_FILE and not info.is_regular_file:
        raise IsADirectoryError("expected a Windows regular file")
    return info


def require_case_insensitive_directory(handle: WindowsHandle) -> None:
    require_opened_kind(handle, WindowsEntryKind.DIRECTORY)
    case_info = _query_handle_info(
        handle,
        FILE_CASE_SENSITIVE_INFORMATION_CLASS,
        FileCaseSensitiveInfo,
    )
    if int(case_info.Flags) & FILE_CS_FLAG_CASE_SENSITIVE_DIR:
        raise OSError("rooted Windows operations reject case-sensitive directories")


def _query_handle_info(
    handle: WindowsHandle,
    information_class: int,
    structure: type[ctypes.Structure],
) -> Any:
    value = structure()
    if not Kernel32.GetFileInformationByHandleEx(
        CHandle(handle.value),
        information_class,
        ctypes.byref(value),
        ctypes.sizeof(value),
    ):
        raise_last_error()
    return value


__all__ = [
    "WindowsFileInfo",
    "query_info",
    "require_case_insensitive_directory",
    "require_file_info_kind",
    "require_opened_kind",
]
