"""Host capability detection for descriptor-rooted POSIX operations."""

from __future__ import annotations

import os

_O_DIRECTORY = getattr(os, "O_DIRECTORY", 0)
_O_NONBLOCK = getattr(os, "O_NONBLOCK", 0)
_O_NOFOLLOW = getattr(os, "O_NOFOLLOW", 0)
_SUPPORTS_ROOTED_OPEN = (
    os.open in os.supports_dir_fd
    and os.stat in os.supports_dir_fd
    and os.stat in os.supports_follow_symlinks
)
_SUPPORTS_ROOTED_MUTATIONS = all(
    function in os.supports_dir_fd
    for function in (
        os.link,
        os.mkdir,
        os.rename,
        os.rmdir,
        os.unlink,
    )
)


def supports_rooted_paths(*, mutations: bool = False) -> bool:
    return bool(
        _O_DIRECTORY
        and _O_NONBLOCK
        and _O_NOFOLLOW
        and _SUPPORTS_ROOTED_OPEN
        and (not mutations or _SUPPORTS_ROOTED_MUTATIONS)
    )


__all__ = ["supports_rooted_paths"]
