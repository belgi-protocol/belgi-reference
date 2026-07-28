"""Security descriptor and readonly-state owner for Windows filesystem handles."""

from __future__ import annotations

import ctypes
from dataclasses import dataclass
from typing import TypeAlias

from .abi import (
    ACL_SIZE_INFORMATION_CLASS,
    DACL_SECURITY_INFORMATION,
    ERROR_INSUFFICIENT_BUFFER,
    ERROR_NO_TOKEN,
    OWNER_SECURITY_INFORMATION,
    PROTECTED_DACL_SECURITY_INFORMATION,
    SDDL_REVISION_1,
    SE_DACL_PRESENT,
    SE_DACL_PROTECTED,
    SE_FILE_OBJECT,
    TOKEN_QUERY,
    TOKEN_USER_INFORMATION_CLASS,
    UNPROTECTED_DACL_SECURITY_INFORMATION,
    AclSizeInformation,
    Advapi32,
    CBool,
    CDword,
    CHandle,
    CVoidPointer,
    Kernel32,
    TokenUser,
    local_free,
    raise_last_error,
    raise_winerror,
)
from .attributes import set_readonly
from .file_info import query_info
from .handle import WindowsHandle

WindowsSecurityToken: TypeAlias = tuple[bytes, bytes | None, bool, bool, bool]


@dataclass(frozen=True, slots=True)
class WindowsSecurityState:
    owner_sid: bytes
    dacl: bytes | None
    dacl_present: bool
    dacl_protected: bool
    readonly: bool

    @property
    def token(self) -> WindowsSecurityToken:
        return (
            self.owner_sid,
            self.dacl,
            self.dacl_present,
            self.dacl_protected,
            self.readonly,
        )


def capture_security_state(handle: WindowsHandle) -> WindowsSecurityState:
    owner = CVoidPointer()
    dacl = CVoidPointer()
    descriptor = CVoidPointer()
    result = int(
        Advapi32.GetSecurityInfo(
            CHandle(handle.value),
            SE_FILE_OBJECT,
            OWNER_SECURITY_INFORMATION | DACL_SECURITY_INFORMATION,
            ctypes.byref(owner),
            None,
            ctypes.byref(dacl),
            None,
            ctypes.byref(descriptor),
        )
    )
    if result:
        raise_winerror(result)
    if not owner.value or not descriptor.value:
        local_free(descriptor)
        raise OSError("Windows security query returned no owner or descriptor")
    try:
        control_value = ctypes.c_uint16()
        revision = CDword()
        if not Advapi32.GetSecurityDescriptorControl(
            descriptor,
            ctypes.byref(control_value),
            ctypes.byref(revision),
        ):
            raise_last_error()
        control = int(control_value.value)
        return WindowsSecurityState(
            owner_sid=_copy_sid(owner),
            dacl=_copy_acl(dacl) if dacl.value else None,
            dacl_present=bool(control & SE_DACL_PRESENT),
            dacl_protected=bool(control & SE_DACL_PROTECTED),
            readonly=query_info(handle).is_readonly,
        )
    finally:
        local_free(descriptor)


def apply_security_state(handle: WindowsHandle, state: WindowsSecurityState) -> None:
    if not state.dacl_present:
        raise OSError(
            "restoring a Windows security state without a DACL is unsupported"
        )
    owner_buffer = ctypes.create_string_buffer(state.owner_sid)
    dacl_buffer = ctypes.create_string_buffer(state.dacl) if state.dacl else None
    information = OWNER_SECURITY_INFORMATION | DACL_SECURITY_INFORMATION
    information |= (
        PROTECTED_DACL_SECURITY_INFORMATION
        if state.dacl_protected
        else UNPROTECTED_DACL_SECURITY_INFORMATION
    )
    result = int(
        Advapi32.SetSecurityInfo(
            CHandle(handle.value),
            SE_FILE_OBJECT,
            information,
            ctypes.cast(owner_buffer, CVoidPointer),
            None,
            ctypes.cast(dacl_buffer, CVoidPointer) if dacl_buffer else None,
            None,
        )
    )
    if result:
        raise_winerror(result)
    set_readonly(handle, state.readonly)
    verify_security_state(handle, state)


def windows_security_state_token(
    handle: WindowsHandle,
) -> WindowsSecurityToken:
    return capture_security_state(handle).token


def verify_security_state(
    handle: WindowsHandle,
    expected: WindowsSecurityState,
) -> None:
    if windows_security_state_token(handle) != expected.token:
        raise PermissionError("Windows security state changed")


def apply_owner_only_dacl(
    handle: WindowsHandle,
    *,
    writable: bool = True,
) -> None:
    info = query_info(handle)
    descriptor = owner_only_security_descriptor(directory=info.is_directory)
    token_sid = _current_token_user_sid()
    owner_buffer = ctypes.create_string_buffer(token_sid)
    try:
        dacl = _security_descriptor_dacl(descriptor)
        result = int(
            Advapi32.SetSecurityInfo(
                CHandle(handle.value),
                SE_FILE_OBJECT,
                OWNER_SECURITY_INFORMATION
                | DACL_SECURITY_INFORMATION
                | PROTECTED_DACL_SECURITY_INFORMATION,
                ctypes.cast(owner_buffer, CVoidPointer),
                None,
                dacl,
                None,
            )
        )
        if result:
            raise_winerror(result)
    finally:
        local_free(descriptor)
    if not info.is_directory:
        set_readonly(handle, not writable)
    verify_owner_only_dacl(handle, writable=None if info.is_directory else writable)


def verify_owner_only_dacl(
    handle: WindowsHandle,
    *,
    writable: bool | None = None,
) -> None:
    info = query_info(handle)
    actual = capture_security_state(handle)
    token_sid = _current_token_user_sid()
    descriptor = owner_only_security_descriptor(directory=info.is_directory)
    try:
        expected_dacl = _copy_acl(_security_descriptor_dacl(descriptor))
    finally:
        local_free(descriptor)
    if (
        actual.owner_sid != token_sid
        or not actual.dacl_present
        or not actual.dacl_protected
        or actual.dacl != expected_dacl
    ):
        raise PermissionError("Windows private object security is not owner-only")
    if writable is not None and actual.readonly == writable:
        state = "writable" if writable else "readonly"
        raise PermissionError(f"Windows private file is not {state}")


def owner_only_security_descriptor(*, directory: bool) -> CVoidPointer:
    inheritance = "OICI" if directory else ""
    sid = _current_token_user_sid()
    if len(sid) < 8 or sid[0] != 1 or len(sid) != 8 + 4 * sid[1]:
        raise ValueError("invalid Windows SID")
    authority = int.from_bytes(sid[2:8], "big")
    subauthorities = [
        int.from_bytes(sid[8 + index * 4 : 12 + index * 4], "little")
        for index in range(sid[1])
    ]
    sid_text = f"S-1-{authority}" + "".join(
        f"-{subauthority}" for subauthority in subauthorities
    )
    sddl = f"O:{sid_text}D:P(A;{inheritance};FA;;;{sid_text})"
    descriptor = CVoidPointer()
    size = CDword()
    if not Advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW(
        sddl,
        SDDL_REVISION_1,
        ctypes.byref(descriptor),
        ctypes.byref(size),
    ):
        raise_last_error()
    if not descriptor.value:
        raise OSError("Windows SDDL conversion returned no descriptor")
    return descriptor


def _security_descriptor_dacl(descriptor: CVoidPointer) -> CVoidPointer:
    present = CBool()
    defaulted = CBool()
    dacl = CVoidPointer()
    if not Advapi32.GetSecurityDescriptorDacl(
        descriptor,
        ctypes.byref(present),
        ctypes.byref(dacl),
        ctypes.byref(defaulted),
    ):
        raise_last_error()
    if not present.value or not dacl.value:
        raise PermissionError("owner-only security descriptor has no DACL")
    return dacl


def _current_token_user_sid() -> bytes:
    token = CHandle()
    if not Advapi32.OpenThreadToken(
        Kernel32.GetCurrentThread(), TOKEN_QUERY, True, ctypes.byref(token)
    ):
        getter = getattr(ctypes, "get_last_error", lambda: 1)
        error = int(getter())
        if error != ERROR_NO_TOKEN:
            raise_winerror(error)
        if not Advapi32.OpenProcessToken(
            Kernel32.GetCurrentProcess(), TOKEN_QUERY, ctypes.byref(token)
        ):
            raise_last_error()
    token_handle = WindowsHandle(int(token.value or 0))
    with token_handle:
        needed = CDword()
        Advapi32.GetTokenInformation(
            CHandle(token_handle.value),
            TOKEN_USER_INFORMATION_CLASS,
            None,
            0,
            ctypes.byref(needed),
        )
        getter = getattr(ctypes, "get_last_error", lambda: 1)
        if int(getter()) != ERROR_INSUFFICIENT_BUFFER or not needed.value:
            raise_last_error()
        buffer = ctypes.create_string_buffer(int(needed.value))
        if not Advapi32.GetTokenInformation(
            CHandle(token_handle.value),
            TOKEN_USER_INFORMATION_CLASS,
            buffer,
            needed,
            ctypes.byref(needed),
        ):
            raise_last_error()
        user = ctypes.cast(buffer, ctypes.POINTER(TokenUser)).contents
        return _copy_sid(user.User.Sid)


def _copy_sid(sid: CVoidPointer) -> bytes:
    length = int(Advapi32.GetLengthSid(sid))
    if length <= 0:
        raise_last_error()
    return ctypes.string_at(sid, length)


def _copy_acl(dacl: CVoidPointer) -> bytes:
    information = AclSizeInformation()
    if not Advapi32.GetAclInformation(
        dacl,
        ctypes.byref(information),
        ctypes.sizeof(information),
        ACL_SIZE_INFORMATION_CLASS,
    ):
        raise_last_error()
    if information.AclBytesInUse < 8:
        raise PermissionError("Windows DACL has an invalid byte length")
    return ctypes.string_at(dacl, int(information.AclBytesInUse))


__all__ = [
    "WindowsSecurityState",
    "WindowsSecurityToken",
    "apply_owner_only_dacl",
    "apply_security_state",
    "capture_security_state",
    "verify_owner_only_dacl",
    "verify_security_state",
    "windows_security_state_token",
]
