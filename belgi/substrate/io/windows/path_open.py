"""Handle-relative, no-follow path opening for Windows rooted IO."""

from __future__ import annotations

import ctypes
from pathlib import Path

from belgi.substrate.io.exceptions import WindowsReparsePointError

from .abi import (
    FILE_FLAG_BACKUP_SEMANTICS,
    FILE_FLAG_OPEN_REPARSE_POINT,
    INVALID_HANDLE_VALUE,
    OBJ_CASE_INSENSITIVE,
    OBJ_DONT_REPARSE,
    OPEN_EXISTING,
    STATUS_REPARSE_POINT_ENCOUNTERED,
    CHandle,
    IoStatusBlock,
    Kernel32,
    Ntdll,
    ObjectAttributes,
    UnicodeString,
    handle_value,
    nt_success,
    raise_last_error,
    raise_ntstatus,
    unsigned_status,
)
from .access import (
    WindowsAccess,
    WindowsEntryKind,
    WindowsShareMode,
    desired_access,
    open_options,
    share_access,
)
from .file_info import (
    query_info,
    require_case_insensitive_directory,
    require_opened_kind,
)
from .handle import WindowsHandle


def validate_component(component: str) -> None:
    if (
        not component
        or component in {".", ".."}
        or any(character in component for character in ("\\", "/", "\0", ":"))
        or component.endswith((".", " "))
    ):
        raise ValueError(f"invalid rooted Windows path component: {component!r}")
    if len(component.encode("utf-16-le")) > 65_532:
        raise ValueError("rooted Windows path component is too long")


def open_windows_root_directory(
    path: Path,
    *,
    access: WindowsAccess = WindowsAccess.INSPECT,
    share_mode: WindowsShareMode = WindowsShareMode.ALLOW_DELETE,
) -> WindowsHandle:
    if not path.is_absolute():
        raise ValueError(f"Windows root path must be absolute: {path}")
    path_text = str(path)
    if not path_text.startswith("\\\\?\\"):
        if path_text.startswith("\\\\"):
            path_text = "\\\\?\\UNC\\" + path_text[2:]
        else:
            path_text = "\\\\?\\" + path_text
    raw = Kernel32.CreateFileW(
        path_text,
        desired_access(access, kind=WindowsEntryKind.DIRECTORY),
        share_access(share_mode),
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT,
        None,
    )
    value = handle_value(raw)
    if value in {0, INVALID_HANDLE_VALUE}:
        raise_last_error()
    handle = WindowsHandle(value)
    try:
        require_case_insensitive_directory(handle)
    except BaseException:
        handle.close()
        raise
    return handle


def open_relative(
    parent: WindowsHandle,
    component: str,
    *,
    kind: WindowsEntryKind,
    access: WindowsAccess = WindowsAccess.INSPECT,
    share_mode: WindowsShareMode = WindowsShareMode.ALLOW_DELETE,
) -> WindowsHandle:
    return _open_relative(
        parent,
        component,
        kind=kind,
        access=access,
        share_mode=share_mode,
        reject=True,
    )


def open_relative_reparse_point(
    parent: WindowsHandle,
    component: str,
    *,
    access: WindowsAccess = WindowsAccess.INSPECT | WindowsAccess.DELETE,
    share_mode: WindowsShareMode = WindowsShareMode.ALLOW_DELETE,
) -> WindowsHandle:
    handle = _open_relative(
        parent,
        component,
        kind=WindowsEntryKind.ANY,
        access=access,
        share_mode=share_mode,
        reject=False,
    )
    if not query_info(handle).is_reparse_point:
        handle.close()
        raise ValueError(f"expected a Windows reparse point: {component}")
    return handle


def relative_entry_exists(parent: WindowsHandle, component: str) -> bool:
    try:
        handle = open_relative(parent, component, kind=WindowsEntryKind.ANY)
    except FileNotFoundError:
        return False
    handle.close()
    return True


def unicode_string(
    component: str,
) -> tuple[ctypes.Array[ctypes.c_wchar], UnicodeString]:
    buffer = ctypes.create_unicode_buffer(component)
    length = len(component.encode("utf-16-le"))
    return buffer, UnicodeString(
        Length=length,
        MaximumLength=length + 2,
        Buffer=ctypes.cast(buffer, ctypes.c_wchar_p),
    )


def _open_relative(
    parent: WindowsHandle,
    component: str,
    *,
    kind: WindowsEntryKind,
    access: WindowsAccess,
    share_mode: WindowsShareMode,
    reject: bool,
) -> WindowsHandle:
    require_case_insensitive_directory(parent)
    validate_component(component)
    name_buffer, name = unicode_string(component)
    attributes = ObjectAttributes(
        ctypes.sizeof(ObjectAttributes),
        CHandle(parent.value),
        ctypes.pointer(name),
        OBJ_CASE_INSENSITIVE | (OBJ_DONT_REPARSE if reject else 0),
        None,
        None,
    )
    raw = CHandle()
    io_status = IoStatusBlock()
    status = int(
        Ntdll.NtOpenFile(
            ctypes.byref(raw),
            desired_access(access, kind=kind),
            ctypes.byref(attributes),
            ctypes.byref(io_status),
            share_access(share_mode),
            open_options(kind),
        )
    )
    del name_buffer
    if not nt_success(status):
        if unsigned_status(status) == STATUS_REPARSE_POINT_ENCOUNTERED:
            raise WindowsReparsePointError(
                f"Windows reparse point not allowed: {component}"
            )
        raise_ntstatus(status)
    handle = WindowsHandle(handle_value(raw))
    try:
        require_opened_kind(handle, kind, reject_reparse=reject)
        if kind is WindowsEntryKind.DIRECTORY and reject:
            require_case_insensitive_directory(handle)
    except BaseException:
        handle.close()
        raise
    return handle


__all__ = [
    "open_relative",
    "open_relative_reparse_point",
    "open_windows_root_directory",
    "relative_entry_exists",
    "unicode_string",
    "validate_component",
]
