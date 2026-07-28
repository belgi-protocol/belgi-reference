from __future__ import annotations

import re
from urllib.parse import urlsplit


def is_absolute_uri(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if any(
        ord(character) > 0x7F or ord(character) <= 0x20 or character in '<>"{}|\\^`'
        for character in value
    ):
        return False
    if re.search(r"%(?![0-9A-Fa-f]{2})", value) is not None:
        return False
    try:
        parsed = urlsplit(value)
        if parsed.port is not None and not (0 <= parsed.port <= 65535):
            return False
    except ValueError:
        return False
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9+.-]*", parsed.scheme) is None:
        return False
    return parsed.scheme.lower() not in {"http", "https"} or bool(parsed.netloc)
