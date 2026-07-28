"""Canonical authentication values for handle-rooted Windows filesystem IO.

Directory authentication binds namespace identity, file attributes, pending
deletion state, and the canonical security token.  Atomic callers that
deliberately replace a directory DACL must explicitly replace their expected
authentication only after validating the new security state.

Regular-file snapshot authentication binds file metadata.  Atomic-file
authentication composes that value with a required security token so atomic
callers cannot accidentally create a metadata-only authentication value.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, TypeVar

from belgi.substrate.io.rooted import FilesystemIdentity

from .access import WindowsEntryKind
from .file_info import WindowsFileInfo, query_info, require_file_info_kind
from .handle import WindowsHandle
from .security import (
    WindowsSecurityState,
    WindowsSecurityToken,
    capture_security_state,
)


@dataclass(frozen=True, slots=True)
class WindowsDirectoryAuthentication:
    identity: FilesystemIdentity
    attributes: int
    delete_pending: bool
    security_token: WindowsSecurityToken


@dataclass(frozen=True, slots=True)
class WindowsRegularFileAuthentication:
    identity: FilesystemIdentity
    attributes: int
    end_of_file: int
    last_write_time: int
    change_time: int
    delete_pending: bool


@dataclass(frozen=True, slots=True)
class WindowsAtomicFileAuthentication:
    regular_file: WindowsRegularFileAuthentication
    security_token: WindowsSecurityToken

    @property
    def identity(self) -> FilesystemIdentity:
        return self.regular_file.identity


_HandleAuthentication = TypeVar("_HandleAuthentication", covariant=True)


class _AuthenticationBuilder(Protocol[_HandleAuthentication]):
    def __call__(
        self,
        info: WindowsFileInfo,
        *,
        security_token: WindowsSecurityToken,
    ) -> _HandleAuthentication: ...


def windows_directory_authentication(
    info: WindowsFileInfo,
    *,
    security_token: WindowsSecurityToken,
) -> WindowsDirectoryAuthentication:
    return WindowsDirectoryAuthentication(
        identity=info.identity,
        attributes=info.attributes,
        delete_pending=info.delete_pending,
        security_token=security_token,
    )


def windows_regular_file_authentication(
    info: WindowsFileInfo,
) -> WindowsRegularFileAuthentication:
    return WindowsRegularFileAuthentication(
        identity=info.identity,
        attributes=info.attributes,
        end_of_file=info.end_of_file,
        last_write_time=info.last_write_time,
        change_time=info.change_time,
        delete_pending=info.delete_pending,
    )


def windows_atomic_file_authentication(
    info: WindowsFileInfo,
    *,
    security_token: WindowsSecurityToken,
) -> WindowsAtomicFileAuthentication:
    return WindowsAtomicFileAuthentication(
        regular_file=windows_regular_file_authentication(info),
        security_token=security_token,
    )


def capture_windows_atomic_file_authentication(
    handle: WindowsHandle,
) -> tuple[
    WindowsFileInfo,
    WindowsSecurityState,
    WindowsAtomicFileAuthentication,
]:
    return _capture_stable_handle_authentication(
        handle,
        kind=WindowsEntryKind.REGULAR_FILE,
        build=windows_atomic_file_authentication,
        label="atomic file",
    )


def capture_windows_directory_authentication(
    handle: WindowsHandle,
) -> tuple[
    WindowsFileInfo,
    WindowsSecurityState,
    WindowsDirectoryAuthentication,
]:
    return _capture_stable_handle_authentication(
        handle,
        kind=WindowsEntryKind.DIRECTORY,
        build=windows_directory_authentication,
        label="directory",
    )


def _capture_stable_handle_authentication(
    handle: WindowsHandle,
    *,
    kind: WindowsEntryKind,
    build: _AuthenticationBuilder[_HandleAuthentication],
    label: str,
) -> tuple[WindowsFileInfo, WindowsSecurityState, _HandleAuthentication]:
    first_info = require_file_info_kind(query_info(handle), kind)
    first_security = capture_security_state(handle)
    first = build(
        first_info,
        security_token=first_security.token,
    )
    final_info = require_file_info_kind(query_info(handle), kind)
    final_security = capture_security_state(handle)
    final = build(
        final_info,
        security_token=final_security.token,
    )
    if final != first:
        raise ValueError(f"Windows {label} authentication changed during capture")
    return final_info, final_security, final


__all__ = [
    "WindowsAtomicFileAuthentication",
    "WindowsDirectoryAuthentication",
    "WindowsRegularFileAuthentication",
    "capture_windows_atomic_file_authentication",
    "capture_windows_directory_authentication",
    "windows_atomic_file_authentication",
    "windows_directory_authentication",
    "windows_regular_file_authentication",
]
