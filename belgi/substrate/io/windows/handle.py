"""RAII ownership for native Windows handles."""

from __future__ import annotations

from collections.abc import Sequence

from .abi import (
    INVALID_HANDLE_VALUE,
    CHandle,
    Ntdll,
    nt_success,
    raise_ntstatus,
)


class WindowsHandle:
    __slots__ = ("_value",)

    def __init__(self, value: int) -> None:
        if value in {-1, 0, INVALID_HANDLE_VALUE}:
            raise ValueError("invalid Windows handle")
        self._value = value

    @property
    def value(self) -> int:
        if self._value == 0:
            raise ValueError("Windows handle is closed")
        return self._value

    @property
    def closed(self) -> bool:
        return self._value == 0

    def close(self) -> None:
        if self._value == 0:
            return
        status = int(Ntdll.NtClose(CHandle(self._value)))
        if not nt_success(status):
            raise_ntstatus(status)
        self._value = 0

    def detach(self) -> int:
        value = self.value
        self._value = 0
        return value

    def __enter__(self) -> WindowsHandle:
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def __del__(self) -> None:
        value = getattr(self, "_value", 0)
        if value:
            try:
                Ntdll.NtClose(CHandle(value))
            except BaseException:
                pass
            self._value = 0


def close_windows_handles(handles: Sequence[WindowsHandle]) -> None:
    first_error: BaseException | None = None
    for handle in reversed(handles):
        try:
            handle.close()
        except BaseException as error:
            if first_error is None:
                first_error = error
    if first_error is not None:
        raise first_error


__all__ = ["WindowsHandle", "close_windows_handles"]
