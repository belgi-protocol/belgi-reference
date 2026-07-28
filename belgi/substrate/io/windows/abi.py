"""ctypes ABI declarations for the Windows-native filesystem owner family."""

# ruff: noqa: RUF012

from __future__ import annotations

import ctypes
from typing import Any, NoReturn


class _UnavailableFunction:
    argtypes: object = None
    restype: object = None

    def __call__(self, *_args: object, **_kwargs: object) -> NoReturn:
        raise OSError("Windows-native filesystem APIs require Windows")


class _UnavailableLibrary:
    def __init__(self) -> None:
        self.functions: dict[str, _UnavailableFunction] = {}

    def __getattr__(self, name: str) -> _UnavailableFunction:
        return self.functions.setdefault(name, _UnavailableFunction())


WinDLL: Any = getattr(ctypes, "WinDLL", None)
if WinDLL is None:  # pragma: no cover - non-Windows typecheck/import seam
    Kernel32: Any = _UnavailableLibrary()
    Ntdll: Any = _UnavailableLibrary()
    Advapi32: Any = _UnavailableLibrary()
else:  # pragma: no cover - exercised by hosted Windows tests
    Kernel32 = WinDLL("kernel32", use_last_error=True)
    Ntdll = WinDLL("ntdll", use_last_error=True)
    Advapi32 = WinDLL("advapi32", use_last_error=True)

CBoolean = ctypes.c_ubyte
CBool = ctypes.c_int32
CDword = ctypes.c_uint32
CLong = ctypes.c_int32
CUlong = ctypes.c_uint32
CUshort = ctypes.c_uint16
CUlonglong = ctypes.c_uint64
CUlongPtr = ctypes.c_size_t
CHandle = ctypes.c_void_p
CVoidPointer = ctypes.c_void_p

INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

FILE_READ_DATA = 0x0001
FILE_LIST_DIRECTORY = 0x0001
FILE_WRITE_DATA = 0x0002
FILE_ADD_FILE = 0x0002
FILE_ADD_SUBDIRECTORY = 0x0004
FILE_TRAVERSE = 0x0020
FILE_DELETE_CHILD = 0x0040
FILE_READ_ATTRIBUTES = 0x0080
FILE_WRITE_ATTRIBUTES = 0x0100
DELETE_ACCESS = 0x00010000
READ_CONTROL = 0x00020000
WRITE_DAC = 0x00040000
WRITE_OWNER = 0x00080000
SYNCHRONIZE = 0x00100000

FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
FILE_SHARE_ALL = FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE
OPEN_EXISTING = 3
FILE_ATTRIBUTE_READONLY = 0x00000001
FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
OBJ_CASE_INSENSITIVE = 0x00000040
OBJ_DONT_REPARSE = 0x00001000
FILE_DIRECTORY_FILE = 0x00000001
FILE_SYNCHRONOUS_IO_NONALERT = 0x00000020
FILE_NON_DIRECTORY_FILE = 0x00000040
FILE_OPEN_REPARSE_POINT = 0x00200000
FILE_CREATE = 2

FILE_BASIC_INFORMATION_CLASS = 0
FILE_STANDARD_INFORMATION_CLASS = 1
FILE_ATTRIBUTE_TAG_INFORMATION_CLASS = 9
FILE_ID_INFORMATION_CLASS = 18
FILE_CASE_SENSITIVE_INFORMATION_CLASS = 23
FILE_CS_FLAG_CASE_SENSITIVE_DIR = 0x00000001
NT_FILE_BASIC_INFORMATION_CLASS = 4
NT_FILE_NAMES_INFORMATION_CLASS = 12
NT_FILE_DISPOSITION_INFORMATION_CLASS = 13
NT_FILE_RENAME_INFORMATION_EX_CLASS = 65
FILE_RENAME_REPLACE_IF_EXISTS = 0x00000001
FILE_RENAME_POSIX_SEMANTICS = 0x00000002
FILE_RENAME_IGNORE_READONLY_ATTRIBUTE = 0x00000040

STATUS_BUFFER_OVERFLOW = 0x80000005
STATUS_NO_MORE_FILES = 0x80000006
STATUS_REPARSE_POINT_ENCOUNTERED = 0xC000050B

SE_FILE_OBJECT = 1
OWNER_SECURITY_INFORMATION = 0x00000001
DACL_SECURITY_INFORMATION = 0x00000004
PROTECTED_DACL_SECURITY_INFORMATION = 0x80000000
UNPROTECTED_DACL_SECURITY_INFORMATION = 0x20000000
SE_DACL_PRESENT = 0x0004
SE_DACL_PROTECTED = 0x1000
ACL_SIZE_INFORMATION_CLASS = 2
TOKEN_QUERY = 0x0008
TOKEN_USER_INFORMATION_CLASS = 1
SDDL_REVISION_1 = 1
ERROR_NO_TOKEN = 1008
ERROR_INSUFFICIENT_BUFFER = 122


class UnicodeString(ctypes.Structure):
    _fields_ = [
        ("Length", CUshort),
        ("MaximumLength", CUshort),
        ("Buffer", ctypes.c_wchar_p),
    ]


class ObjectAttributes(ctypes.Structure):
    _fields_ = [
        ("Length", CUlong),
        ("RootDirectory", CHandle),
        ("ObjectName", ctypes.POINTER(UnicodeString)),
        ("Attributes", CUlong),
        ("SecurityDescriptor", CVoidPointer),
        ("SecurityQualityOfService", CVoidPointer),
    ]


class IoStatusValue(ctypes.Union):
    _fields_ = [("Status", CLong), ("Pointer", CVoidPointer)]


class IoStatusBlock(ctypes.Structure):
    _anonymous_ = ("Value",)
    _fields_ = [("Value", IoStatusValue), ("Information", CUlongPtr)]


class FileId128(ctypes.Structure):
    _fields_ = [("Identifier", ctypes.c_ubyte * 16)]


class FileIdInfo(ctypes.Structure):
    _fields_ = [("VolumeSerialNumber", CUlonglong), ("FileId", FileId128)]


class FileAttributeTagInfo(ctypes.Structure):
    _fields_ = [("FileAttributes", CDword), ("ReparseTag", CDword)]


class FileBasicInfo(ctypes.Structure):
    _fields_ = [
        ("CreationTime", ctypes.c_int64),
        ("LastAccessTime", ctypes.c_int64),
        ("LastWriteTime", ctypes.c_int64),
        ("ChangeTime", ctypes.c_int64),
        ("FileAttributes", CDword),
    ]


class FileStandardInfo(ctypes.Structure):
    _fields_ = [
        ("AllocationSize", ctypes.c_int64),
        ("EndOfFile", ctypes.c_int64),
        ("NumberOfLinks", CDword),
        ("DeletePending", CBoolean),
        ("Directory", CBoolean),
    ]


class FileCaseSensitiveInfo(ctypes.Structure):
    _fields_ = [("Flags", CDword)]


class FileDispositionInformation(ctypes.Structure):
    _fields_ = [("DeleteFile", CBoolean)]


class FileRenameInformationEx(ctypes.Structure):
    _fields_ = [
        ("Flags", CUlong),
        ("RootDirectory", CHandle),
        ("FileNameLength", CUlong),
        ("FileName", ctypes.c_wchar * 1),
    ]


class AclSizeInformation(ctypes.Structure):
    _fields_ = [
        ("AceCount", CDword),
        ("AclBytesInUse", CDword),
        ("AclBytesFree", CDword),
    ]


class SidAndAttributes(ctypes.Structure):
    _fields_ = [("Sid", CVoidPointer), ("Attributes", CDword)]


class TokenUser(ctypes.Structure):
    _fields_ = [("User", SidAndAttributes)]


Kernel32.CreateFileW.argtypes = [
    ctypes.c_wchar_p,
    CDword,
    CDword,
    CVoidPointer,
    CDword,
    CDword,
    CHandle,
]
Kernel32.CreateFileW.restype = CHandle
Kernel32.GetFileInformationByHandleEx.argtypes = [
    CHandle,
    ctypes.c_int,
    CVoidPointer,
    CDword,
]
Kernel32.GetFileInformationByHandleEx.restype = CBool
Kernel32.FlushFileBuffers.argtypes = [CHandle]
Kernel32.FlushFileBuffers.restype = CBool
Kernel32.GetCurrentProcess.argtypes = []
Kernel32.GetCurrentProcess.restype = CHandle
Kernel32.GetCurrentThread.argtypes = []
Kernel32.GetCurrentThread.restype = CHandle
Kernel32.LocalFree.argtypes = [CVoidPointer]
Kernel32.LocalFree.restype = CVoidPointer

Ntdll.NtOpenFile.argtypes = [
    ctypes.POINTER(CHandle),
    CDword,
    ctypes.POINTER(ObjectAttributes),
    ctypes.POINTER(IoStatusBlock),
    CUlong,
    CUlong,
]
Ntdll.NtOpenFile.restype = CLong
Ntdll.NtCreateFile.argtypes = [
    ctypes.POINTER(CHandle),
    CDword,
    ctypes.POINTER(ObjectAttributes),
    ctypes.POINTER(IoStatusBlock),
    CVoidPointer,
    CUlong,
    CUlong,
    CUlong,
    CUlong,
    CVoidPointer,
    CUlong,
]
Ntdll.NtCreateFile.restype = CLong
Ntdll.NtSetInformationFile.argtypes = [
    CHandle,
    ctypes.POINTER(IoStatusBlock),
    CVoidPointer,
    CUlong,
    ctypes.c_int,
]
Ntdll.NtSetInformationFile.restype = CLong
Ntdll.NtQueryDirectoryFile.argtypes = [
    CHandle,
    CHandle,
    CVoidPointer,
    CVoidPointer,
    ctypes.POINTER(IoStatusBlock),
    CVoidPointer,
    CUlong,
    ctypes.c_int,
    CBoolean,
    CVoidPointer,
    CBoolean,
]
Ntdll.NtQueryDirectoryFile.restype = CLong
Ntdll.NtClose.argtypes = [CHandle]
Ntdll.NtClose.restype = CLong
Ntdll.RtlNtStatusToDosError.argtypes = [CLong]
Ntdll.RtlNtStatusToDosError.restype = CUlong

Advapi32.OpenThreadToken.argtypes = [CHandle, CDword, CBool, ctypes.POINTER(CHandle)]
Advapi32.OpenThreadToken.restype = CBool
Advapi32.OpenProcessToken.argtypes = [CHandle, CDword, ctypes.POINTER(CHandle)]
Advapi32.OpenProcessToken.restype = CBool
Advapi32.GetTokenInformation.argtypes = [
    CHandle,
    ctypes.c_int,
    CVoidPointer,
    CDword,
    ctypes.POINTER(CDword),
]
Advapi32.GetTokenInformation.restype = CBool
Advapi32.ConvertSidToStringSidW.argtypes = [CVoidPointer, ctypes.POINTER(CVoidPointer)]
Advapi32.ConvertSidToStringSidW.restype = CBool
Advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [
    ctypes.c_wchar_p,
    CDword,
    ctypes.POINTER(CVoidPointer),
    ctypes.POINTER(CDword),
]
Advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW.restype = CBool
Advapi32.GetSecurityDescriptorDacl.argtypes = [
    CVoidPointer,
    ctypes.POINTER(CBool),
    ctypes.POINTER(CVoidPointer),
    ctypes.POINTER(CBool),
]
Advapi32.GetSecurityDescriptorDacl.restype = CBool
Advapi32.GetSecurityDescriptorControl.argtypes = [
    CVoidPointer,
    ctypes.POINTER(CUshort),
    ctypes.POINTER(CDword),
]
Advapi32.GetSecurityDescriptorControl.restype = CBool
Advapi32.GetAclInformation.argtypes = [CVoidPointer, CVoidPointer, CDword, ctypes.c_int]
Advapi32.GetAclInformation.restype = CBool
Advapi32.GetSecurityInfo.argtypes = [
    CHandle,
    ctypes.c_int,
    CDword,
    ctypes.POINTER(CVoidPointer),
    ctypes.POINTER(CVoidPointer),
    ctypes.POINTER(CVoidPointer),
    ctypes.POINTER(CVoidPointer),
    ctypes.POINTER(CVoidPointer),
]
Advapi32.GetSecurityInfo.restype = CDword
Advapi32.SetSecurityInfo.argtypes = [
    CHandle,
    ctypes.c_int,
    CDword,
    CVoidPointer,
    CVoidPointer,
    CVoidPointer,
    CVoidPointer,
]
Advapi32.SetSecurityInfo.restype = CDword
Advapi32.GetLengthSid.argtypes = [CVoidPointer]
Advapi32.GetLengthSid.restype = CDword


def handle_value(handle: object) -> int:
    if isinstance(handle, int):
        return handle
    value: Any = getattr(handle, "value", None)
    if not isinstance(value, int):
        raise OSError("Windows API returned an invalid handle")
    return value


def nt_success(status: int) -> bool:
    return unsigned_status(status) < 0x80000000


def unsigned_status(status: int) -> int:
    return status & 0xFFFFFFFF


def raise_ntstatus(status: int) -> NoReturn:
    code = int(Ntdll.RtlNtStatusToDosError(CLong(status)))
    raise_winerror(code)


def raise_last_error() -> NoReturn:
    getter: Any = getattr(ctypes, "get_last_error", lambda: 1)
    raise_winerror(int(getter()))


def raise_winerror(code: int) -> NoReturn:
    factory: Any = getattr(ctypes, "WinError", None)
    if factory is None:
        raise OSError(code, f"WinError {code}")
    raise factory(code)


def local_free(pointer: CVoidPointer) -> None:
    if pointer and pointer.value and Kernel32.LocalFree(pointer):
        raise OSError("LocalFree failed for Windows security buffer")
