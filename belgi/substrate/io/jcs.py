from __future__ import annotations

from typing import Any

import rfc8785


def canonicalize_jcs(value: Any) -> bytes:
    """Return RFC 8785 JSON Canonicalization Scheme bytes."""

    try:
        return rfc8785.dumps(value)
    except (rfc8785.CanonicalizationError, TypeError, ValueError) as exc:
        raise ValueError(f"value is outside the RFC 8785 domain: {exc}") from exc


__all__ = ["canonicalize_jcs"]
