from __future__ import annotations

from collections.abc import Mapping


def required_mapping(
    payload: Mapping[str, object], *, field: str
) -> Mapping[str, object]:
    value = payload.get(field)
    if not isinstance(value, dict):
        raise ValueError(f"Replay-package corpus {field!r} must be an object.")
    return value


def required_mapping_array(
    payload: Mapping[str, object], *, field: str
) -> tuple[Mapping[str, object], ...]:
    value = payload.get(field)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"Replay-package corpus {field!r} must be an object array.")
    return tuple(value)


def required_replay_package_corpus_text(
    payload: Mapping[str, object], *, field: str
) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or value == "":
        raise ValueError(f"Replay-package corpus {field!r} must be text.")
    return value


def optional_replay_package_corpus_text(
    payload: Mapping[str, object], *, field: str
) -> str | None:
    value = payload.get(field)
    if value is not None and not isinstance(value, str):
        raise ValueError(f"Replay-package corpus {field!r} must be text or null.")
    return value


def required_text_array(
    payload: Mapping[str, object], *, field: str
) -> tuple[str, ...]:
    value = payload.get(field)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"Replay-package corpus {field!r} must be a text array.")
    return tuple(value)


def required_int(payload: Mapping[str, object], *, field: str) -> int:
    value = payload.get(field)
    if type(value) is not int:
        raise ValueError(f"Replay-package corpus {field!r} must be an integer.")
    return value


def optional_int(payload: Mapping[str, object], *, field: str) -> int | None:
    value = payload.get(field)
    if value is not None and type(value) is not int:
        raise ValueError(f"Replay-package corpus {field!r} must be an integer or null.")
    return value


def required_bool(payload: Mapping[str, object], *, field: str) -> bool:
    value = payload.get(field)
    if not isinstance(value, bool):
        raise ValueError(f"Replay-package corpus {field!r} must be boolean.")
    return value


def optional_replay_package_corpus_bool(
    payload: Mapping[str, object], *, field: str
) -> bool:
    value = payload.get(field, True)
    if not isinstance(value, bool):
        raise ValueError(f"Replay-package corpus {field!r} must be boolean.")
    return value


def required_hex_bytes(payload: Mapping[str, object], *, field: str) -> bytes:
    text = payload.get(field)
    if not isinstance(text, str):
        raise ValueError(f"Replay-package corpus {field!r} must be text.")
    if len(text) % 2 != 0 or any(
        character not in "0123456789abcdef" for character in text
    ):
        raise ValueError(
            f"Replay-package corpus {field!r} must be lowercase hexadecimal."
        )
    return bytes.fromhex(text)


__all__ = [
    "optional_int",
    "optional_replay_package_corpus_bool",
    "optional_replay_package_corpus_text",
    "required_bool",
    "required_hex_bytes",
    "required_int",
    "required_mapping",
    "required_mapping_array",
    "required_replay_package_corpus_text",
    "required_text_array",
]
