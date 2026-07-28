from __future__ import annotations

from pathlib import Path

from .encoding import render_json_text
from .parsing import parse_json_object, parse_json_value


def load_json_value(path: Path, *, label: str) -> object:
    return parse_json_value(
        path.read_text(encoding="utf-8", errors="strict"),
        label=label,
    )


def load_json_object(path: Path, *, label: str) -> dict[str, object]:
    return parse_json_object(
        path.read_text(encoding="utf-8", errors="strict"),
        label=label,
    )


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_json_text(obj),
        encoding="utf-8",
        errors="strict",
        newline="\n",
    )


__all__ = ["load_json_object", "load_json_value", "write_json"]
