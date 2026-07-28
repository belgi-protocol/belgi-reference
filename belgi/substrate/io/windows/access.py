"""Access-mask and entry-kind policy for Windows filesystem handles."""

from __future__ import annotations

from enum import Enum, IntFlag

from .abi import (
    DELETE_ACCESS,
    FILE_ADD_FILE,
    FILE_ADD_SUBDIRECTORY,
    FILE_DELETE_CHILD,
    FILE_DIRECTORY_FILE,
    FILE_LIST_DIRECTORY,
    FILE_NON_DIRECTORY_FILE,
    FILE_OPEN_REPARSE_POINT,
    FILE_READ_ATTRIBUTES,
    FILE_READ_DATA,
    FILE_SHARE_ALL,
    FILE_SHARE_READ,
    FILE_SHARE_WRITE,
    FILE_SYNCHRONOUS_IO_NONALERT,
    FILE_TRAVERSE,
    FILE_WRITE_ATTRIBUTES,
    FILE_WRITE_DATA,
    READ_CONTROL,
    SYNCHRONIZE,
    WRITE_DAC,
    WRITE_OWNER,
)


class WindowsEntryKind(Enum):
    ANY = "any"
    DIRECTORY = "directory"
    REGULAR_FILE = "regular-file"


class WindowsShareMode(Enum):
    ALLOW_DELETE = "allow-delete"
    PIN_NAMESPACE = "pin-namespace"


class WindowsAccess(IntFlag):
    INSPECT = 1
    READ_DATA = 2
    WRITE_DATA = 4
    DIRECTORY_WRITE = 8
    DELETE = 16
    READ_SECURITY = 32
    WRITE_DACL = 64
    WRITE_OWNER = 128
    WRITE_ATTRIBUTES = 256


def desired_access(access: WindowsAccess, *, kind: WindowsEntryKind) -> int:
    desired = FILE_READ_ATTRIBUTES | SYNCHRONIZE
    if kind is WindowsEntryKind.DIRECTORY:
        desired |= FILE_TRAVERSE | FILE_LIST_DIRECTORY
    if access & WindowsAccess.READ_DATA:
        desired |= FILE_READ_DATA
    if access & WindowsAccess.WRITE_DATA:
        desired |= FILE_WRITE_DATA
    if access & WindowsAccess.DIRECTORY_WRITE:
        desired |= (
            FILE_TRAVERSE | FILE_ADD_FILE | FILE_ADD_SUBDIRECTORY | FILE_DELETE_CHILD
        )
    if access & WindowsAccess.DELETE:
        desired |= DELETE_ACCESS
    if access & WindowsAccess.READ_SECURITY:
        desired |= READ_CONTROL
    if access & WindowsAccess.WRITE_DACL:
        desired |= WRITE_DAC | READ_CONTROL
    if access & WindowsAccess.WRITE_OWNER:
        desired |= WRITE_OWNER
    if access & WindowsAccess.WRITE_ATTRIBUTES:
        desired |= FILE_WRITE_ATTRIBUTES
    return desired


def open_options(kind: WindowsEntryKind) -> int:
    options = FILE_SYNCHRONOUS_IO_NONALERT | FILE_OPEN_REPARSE_POINT
    if kind is WindowsEntryKind.DIRECTORY:
        options |= FILE_DIRECTORY_FILE
    elif kind is WindowsEntryKind.REGULAR_FILE:
        options |= FILE_NON_DIRECTORY_FILE
    return options


def share_access(mode: WindowsShareMode) -> int:
    if mode is WindowsShareMode.PIN_NAMESPACE:
        return FILE_SHARE_READ | FILE_SHARE_WRITE
    return FILE_SHARE_ALL


def is_access_unavailable_error(error: OSError) -> bool:
    return getattr(error, "winerror", None) in {5, 19}


__all__ = [
    "WindowsAccess",
    "WindowsEntryKind",
    "WindowsShareMode",
    "desired_access",
    "is_access_unavailable_error",
    "open_options",
    "share_access",
]
