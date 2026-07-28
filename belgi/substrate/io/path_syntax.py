from __future__ import annotations

from collections.abc import Iterable
from pathlib import PurePosixPath

__all__ = [
    "has_casefold_spelling_collision",
    "is_canonical_relative_posix_path",
    "is_portable_path_segment",
    "is_uri_unreserved_segment",
]


_URI_UNRESERVED = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~"
)
_WINDOWS_INVALID_PATH_CHARACTERS = frozenset('<>:"/\\|?*')
_WINDOWS_RESERVED_DEVICE_BASENAMES = frozenset(
    {"aux", "con", "nul", "prn"}
    | {f"com{number}" for number in range(1, 10)}
    | {f"lpt{number}" for number in range(1, 10)}
)


def is_canonical_relative_posix_path(value: str) -> bool:
    if "\\" in value or any(
        ord(character) < 0x20 or ord(character) == 0x7F for character in value
    ):
        return False
    path = PurePosixPath(value)
    return (
        bool(path.parts)
        and not path.is_absolute()
        and ".." not in path.parts
        and value == value.strip()
        and value == path.as_posix()
    )


def is_uri_unreserved_segment(value: str) -> bool:
    return bool(value) and all(character in _URI_UNRESERVED for character in value)


def is_portable_path_segment(value: str) -> bool:
    if (
        not value
        or value in {".", ".."}
        or value[-1] in {" ", "."}
        or any(
            character in _WINDOWS_INVALID_PATH_CHARACTERS
            or ord(character) < 0x20
            or ord(character) == 0x7F
            for character in value
        )
    ):
        return False
    device_basename = value.partition(".")[0].rstrip(" .").casefold()
    return device_basename not in _WINDOWS_RESERVED_DEVICE_BASENAMES


def has_casefold_spelling_collision(values: Iterable[str]) -> bool:
    spelling_by_folded_value: dict[str, str] = {}
    for value in values:
        folded_value = value.casefold()
        prior = spelling_by_folded_value.setdefault(folded_value, value)
        if prior != value:
            return True
    return False
