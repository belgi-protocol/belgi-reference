from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation

from belgi.substrate.io.jcs import canonicalize_jcs

from .exceptions import JSONDomainError

_MAX_SAFE_INTEGER = 9_007_199_254_740_991


def decode_json_number(token: str) -> int | float:
    """Decode one valid JSON number token inside the bounded binary64 domain."""

    try:
        exact_value = Decimal(token)
        binary64_value = float(token)
    except (InvalidOperation, OverflowError, ValueError) as exc:
        raise JSONDomainError(
            stage="json-syntax",
            code="invalid-number-grammar",
            detail="invalid JSON number token",
        ) from exc

    if not math.isfinite(binary64_value):
        raise JSONDomainError(
            stage="json-domain",
            code="number-overflow",
            detail="JSON number overflows the finite binary64 domain",
        )
    if token.startswith("-") and exact_value.is_zero():
        raise JSONDomainError(
            stage="json-domain",
            code="negative-zero",
            detail="negative-zero JSON spellings are not admitted",
        )
    if not exact_value.is_zero() and binary64_value == 0.0:
        raise JSONDomainError(
            stage="json-domain",
            code="number-underflow",
            detail="nonzero JSON number underflows to binary64 zero",
        )
    if exact_value == exact_value.to_integral_value() and abs(exact_value) > Decimal(
        _MAX_SAFE_INTEGER
    ):
        raise JSONDomainError(
            stage="json-domain",
            code="unsafe-integral-value",
            detail="integral JSON number is outside the safe binary64 interval",
        )

    canonical_token = canonicalize_jcs(binary64_value).decode("ascii")
    if exact_value != Decimal(canonical_token):
        raise JSONDomainError(
            stage="json-domain",
            code="number-precision-loss",
            detail="JSON number is not preserved by binary64 JCS serialization",
        )

    if "." not in token and "e" not in token.lower():
        return int(token)
    return binary64_value


__all__ = ["decode_json_number"]
