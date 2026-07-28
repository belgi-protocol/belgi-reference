from __future__ import annotations

from pathlib import Path

__all__ = ["render_filesystem_path"]


def render_filesystem_path(path: Path | str) -> str:
    rendered: list[str] = []
    for character in str(path):
        codepoint = ord(character)
        if character == "\\":
            rendered.append("\\\\")
        elif codepoint < 0x20 or codepoint == 0x7F:
            rendered.append(f"\\x{codepoint:02x}")
        elif 0xDC80 <= codepoint <= 0xDCFF:
            rendered.append(f"\\x{codepoint - 0xDC00:02x}")
        else:
            rendered.append(character)
    return "".join(rendered)
