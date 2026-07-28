from __future__ import annotations

import json
from typing import Any


def canonical_json_text(obj: Any) -> str:
    return json.dumps(
        obj,
        allow_nan=False,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_json_bytes(obj: Any) -> bytes:
    """Return canonical JSON bytes with a trailing line feed."""

    return (canonical_json_text(obj) + "\n").encode("utf-8", errors="strict")


def render_json_text(
    obj: Any,
    *,
    sort_keys: bool = True,
    indent: int | None = 2,
    separators: tuple[str, str] | None = None,
) -> str:
    if separators is None:
        return (
            json.dumps(
                obj,
                allow_nan=False,
                ensure_ascii=False,
                sort_keys=sort_keys,
                indent=indent,
            )
            + "\n"
        )
    return (
        json.dumps(
            obj,
            allow_nan=False,
            ensure_ascii=False,
            sort_keys=sort_keys,
            indent=indent,
            separators=separators,
        )
        + "\n"
    )


def render_json_bytes(
    obj: Any,
    *,
    sort_keys: bool = True,
    indent: int | None = 2,
    separators: tuple[str, str] | None = None,
) -> bytes:
    return render_json_text(
        obj,
        sort_keys=sort_keys,
        indent=indent,
        separators=separators,
    ).encode("utf-8", errors="strict")


__all__ = [
    "canonical_json_bytes",
    "canonical_json_text",
    "render_json_bytes",
    "render_json_text",
]
