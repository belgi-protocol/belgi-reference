"""Exact accepted-set mechanism for BELGI's Ed25519 successor method."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.substrate.hash import sha512_bytes

FIELD_MODULUS = 2**255 - 19
GROUP_ORDER = 2**252 + 27742317777372353535851937790883648493
IDENTITY = (0, 1)
BASE_POINT = (
    15112221349535400772501151409588531511454012693041857206046113283949847762202,
    46316835694926478169428394003475163141307993866256225615783033603165251855960,
)
_CURVE_D = (-121665 * pow(121666, FIELD_MODULUS - 2, FIELD_MODULUS)) % FIELD_MODULUS
_SQRT_MINUS_ONE = pow(2, (FIELD_MODULUS - 1) // 4, FIELD_MODULUS)

Point = tuple[int, int]


@dataclass(frozen=True, slots=True, kw_only=True)
class Ed25519AcceptanceObservation:
    public_key_canonical: bool
    signature_r_canonical: bool
    scalar_canonical: bool
    public_key_exact_order: bool
    uncofactored_equation: bool
    cofactored_equation: bool

    @property
    def accepted(self) -> bool:
        return (
            self.public_key_canonical
            and self.signature_r_canonical
            and self.scalar_canonical
            and self.public_key_exact_order
            and self.uncofactored_equation
        )


def _encode_point(point: Point) -> bytes:
    x, y = point
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def decode_canonical_point(encoded: bytes) -> Point | None:
    if len(encoded) != 32:
        return None
    sign = encoded[31] >> 7
    y = int.from_bytes(encoded, "little") & ((1 << 255) - 1)
    if y >= FIELD_MODULUS:
        return None
    y_squared = y * y % FIELD_MODULUS
    denominator = (_CURVE_D * y_squared + 1) % FIELD_MODULUS
    x_squared = (
        (y_squared - 1)
        * pow(denominator, FIELD_MODULUS - 2, FIELD_MODULUS)
        % FIELD_MODULUS
    )
    x = pow(x_squared, (FIELD_MODULUS + 3) // 8, FIELD_MODULUS)
    if (x * x - x_squared) % FIELD_MODULUS:
        x = x * _SQRT_MINUS_ONE % FIELD_MODULUS
    if (x * x - x_squared) % FIELD_MODULUS or (x == 0 and sign):
        return None
    if x & 1 != sign:
        x = FIELD_MODULUS - x
    point = (x, y)
    return point if _encode_point(point) == encoded else None


def _add_points(left: Point, right: Point) -> Point:
    x1, y1 = left
    x2, y2 = right
    product = _CURVE_D * x1 * x2 * y1 * y2 % FIELD_MODULUS
    x3 = (
        (x1 * y2 + y1 * x2)
        * pow(1 + product, FIELD_MODULUS - 2, FIELD_MODULUS)
        % FIELD_MODULUS
    )
    y3 = (
        (y1 * y2 + x1 * x2)
        * pow(1 - product, FIELD_MODULUS - 2, FIELD_MODULUS)
        % FIELD_MODULUS
    )
    return x3, y3


def _multiply_point(scalar: int, point: Point) -> Point:
    result = IDENTITY
    addend = point
    while scalar:
        if scalar & 1:
            result = _add_points(result, addend)
        addend = _add_points(addend, addend)
        scalar >>= 1
    return result


def has_exact_group_order(point: Point) -> bool:
    return point != IDENTITY and _multiply_point(GROUP_ORDER, point) == IDENTITY


def observe_ed25519_acceptance(
    *, public_key: bytes, message: bytes, signature: bytes
) -> Ed25519AcceptanceObservation:
    if len(public_key) != 32 or len(signature) != 64:
        return Ed25519AcceptanceObservation(
            public_key_canonical=False,
            signature_r_canonical=False,
            scalar_canonical=False,
            public_key_exact_order=False,
            uncofactored_equation=False,
            cofactored_equation=False,
        )
    encoded_r = signature[:32]
    scalar = int.from_bytes(signature[32:], "little")
    public_point = decode_canonical_point(public_key)
    signature_r = decode_canonical_point(encoded_r)
    scalar_canonical = scalar < GROUP_ORDER
    exact_order = public_point is not None and has_exact_group_order(public_point)
    if public_point is None or signature_r is None or not scalar_canonical:
        return Ed25519AcceptanceObservation(
            public_key_canonical=public_point is not None,
            signature_r_canonical=signature_r is not None,
            scalar_canonical=scalar_canonical,
            public_key_exact_order=exact_order,
            uncofactored_equation=False,
            cofactored_equation=False,
        )
    challenge = (
        int.from_bytes(sha512_bytes(encoded_r + public_key + message), "little")
        % GROUP_ORDER
    )
    left = _multiply_point(scalar, BASE_POINT)
    right = _add_points(signature_r, _multiply_point(challenge, public_point))
    return Ed25519AcceptanceObservation(
        public_key_canonical=True,
        signature_r_canonical=True,
        scalar_canonical=True,
        public_key_exact_order=exact_order,
        uncofactored_equation=left == right,
        cofactored_equation=_multiply_point(8, left) == _multiply_point(8, right),
    )


__all__ = [
    "Ed25519AcceptanceObservation",
    "decode_canonical_point",
    "has_exact_group_order",
    "observe_ed25519_acceptance",
]
