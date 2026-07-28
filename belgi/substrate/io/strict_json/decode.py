from __future__ import annotations

import json
import re
from collections.abc import Iterable
from typing import NoReturn

from .exceptions import JSONDomainError
from .numbers import decode_json_number

_JSON_WHITESPACE = " \t\r\n"
_LEADING_ZERO_NUMBER = re.compile(r"-?0[0-9]")


def _reject_nonstandard_constant(token: str) -> NoReturn:
    raise JSONDomainError(
        stage="json-syntax",
        code="invalid-number-grammar",
        detail=f"non-standard JSON number token {token!r}",
    )


def _object_from_unique_pairs(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in pairs:
        if name in result:
            raise JSONDomainError(
                stage="json-domain",
                code="duplicate-object-name",
                detail=f"duplicate decoded JSON object name {name!r}",
            )
        result[name] = value
    return result


def _validate_unicode_text(value: str) -> None:
    for character in value:
        code_point = ord(character)
        if 0xD800 <= code_point <= 0xDFFF:
            raise JSONDomainError(
                stage="json-domain",
                code="invalid-unicode-scalar",
                detail="decoded JSON string contains a surrogate code point",
            )
        if 0xFDD0 <= code_point <= 0xFDEF or (
            code_point <= 0x10FFFF and code_point & 0xFFFF in {0xFFFE, 0xFFFF}
        ):
            raise JSONDomainError(
                stage="json-domain",
                code="unicode-noncharacter",
                detail="decoded JSON string contains a Unicode noncharacter",
            )


def _children(value: object) -> Iterable[tuple[object, int]]:
    if isinstance(value, dict):
        for name, child in value.items():
            _validate_unicode_text(name)
            yield child, 1 if isinstance(child, (dict, list)) else 0
    elif isinstance(value, list):
        for child in value:
            yield child, 1 if isinstance(child, (dict, list)) else 0
    elif isinstance(value, str):
        _validate_unicode_text(value)


def _validate_domain(value: object, *, maximum_depth: int) -> None:
    if maximum_depth < 1:
        raise ValueError("maximum_depth must be positive")
    root_depth = 1 if isinstance(value, (dict, list)) else 0
    pending: list[tuple[object, int]] = [(value, root_depth)]
    while pending:
        current, depth = pending.pop()
        if depth > maximum_depth:
            raise JSONDomainError(
                stage="json-domain",
                code="maximum-nesting-depth",
                detail=f"JSON container nesting exceeds {maximum_depth}",
            )
        for child, depth_increment in _children(current):
            pending.append((child, depth + depth_increment))


def _syntax_code(*, text: str, error: json.JSONDecodeError) -> str:
    stripped = text.lstrip(_JSON_WHITESPACE)
    if (
        stripped.startswith(("+", "NaN", "Infinity", "-Infinity"))
        or _LEADING_ZERO_NUMBER.match(stripped) is not None
    ):
        return "invalid-number-grammar"
    if error.pos >= len(text.rstrip(_JSON_WHITESPACE)) or error.msg.startswith(
        "Unterminated string"
    ):
        return "incomplete-json-text"
    return "invalid-json-syntax"


def decode_strict_json(
    raw: str | bytes,
    *,
    maximum_depth: int = 128,
) -> object:
    """Decode one complete strict UTF-8 JSON text into its admitted value."""

    try:
        text = raw.decode("utf-8", errors="strict") if isinstance(raw, bytes) else raw
    except UnicodeDecodeError as exc:
        raise JSONDomainError(
            stage="utf8",
            code="invalid-utf8",
            detail="candidate bytes are not valid UTF-8",
        ) from exc
    if text.startswith("\ufeff"):
        raise JSONDomainError(
            stage="utf8",
            code="byte-order-mark",
            detail="a leading UTF-8 byte-order mark is not admitted",
        )

    start = len(text) - len(text.lstrip(_JSON_WHITESPACE))
    decoder = json.JSONDecoder(
        object_pairs_hook=_object_from_unique_pairs,
        parse_constant=_reject_nonstandard_constant,
        parse_float=decode_json_number,
        parse_int=decode_json_number,
        strict=True,
    )
    try:
        value, end = decoder.raw_decode(text, idx=start)
    except JSONDomainError:
        raise
    except (RecursionError, json.JSONDecodeError) as exc:
        if isinstance(exc, RecursionError):
            code = "maximum-nesting-depth"
            stage = "json-domain"
        else:
            code = _syntax_code(text=text, error=exc)
            stage = "json-syntax"
        raise JSONDomainError(
            stage=stage,
            code=code,
            detail="candidate is not one complete JSON text",
        ) from exc

    if text[end:].strip(_JSON_WHITESPACE):
        stripped = text.lstrip(_JSON_WHITESPACE)
        code = (
            "invalid-number-grammar"
            if _LEADING_ZERO_NUMBER.match(stripped) is not None
            else "trailing-content"
        )
        raise JSONDomainError(
            stage="json-syntax",
            code=code,
            detail="candidate contains content after the JSON text",
        )
    _validate_domain(value, maximum_depth=maximum_depth)
    return value


__all__ = ["decode_strict_json"]
