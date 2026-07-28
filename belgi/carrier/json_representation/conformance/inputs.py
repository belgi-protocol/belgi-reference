from __future__ import annotations

from collections.abc import Mapping


def required_json_representation_corpus_text(
    payload: Mapping[str, object], *, field: str
) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or value == "":
        raise ValueError(f"JSON representation corpus {field!r} must be text.")
    return value


__all__ = ["required_json_representation_corpus_text"]
