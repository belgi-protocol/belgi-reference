from __future__ import annotations

from collections.abc import Mapping

from belgi.substrate.base64 import decode_canonical_base64
from belgi.substrate.crypto import (
    parse_ed25519_public_key_hex,
    verify_ed25519_signature,
)
from belgi.substrate.ed25519_acceptance import observe_ed25519_acceptance
from belgi.substrate.exceptions import (
    Base64EncodingError,
    Base64LengthError,
    Ed25519KeyError,
    Ed25519PointEncodingError,
    Ed25519PointOrderError,
    Ed25519ScalarEncodingError,
    Ed25519SignatureEncodingError,
    Ed25519SignatureError,
    NonCanonicalBase64Error,
)

from .inputs import lowercase_hex_bytes, required_crypto_corpus_text
from .model import CryptoCaseObservation, accepted, rejected


def observe_ed25519_operation(
    *,
    operation: str,
    payload: Mapping[str, object],
) -> CryptoCaseObservation:
    if operation == "ed25519-verify":
        return _observe_verification(payload=payload)
    if operation == "public-key-validate":
        return _observe_public_key(payload=payload)
    if operation == "signature-base64-validate":
        return _observe_signature_base64(payload=payload)
    raise ValueError(f"Unsupported Ed25519 corpus operation: {operation!r}.")


def _observe_verification(
    *,
    payload: Mapping[str, object],
) -> CryptoCaseObservation:
    if required_crypto_corpus_text(payload=payload, field="variant") != "Ed25519":
        return rejected(reason_code="variant-unsupported")
    public_key_hex = required_crypto_corpus_text(payload=payload, field="publicKeyHex")
    try:
        public_key = parse_ed25519_public_key_hex(public_key_hex)
    except Ed25519PointEncodingError:
        return rejected(reason_code="point-encoding-invalid")
    except Ed25519PointOrderError:
        return rejected(reason_code="public-key-order-invalid")
    except Ed25519KeyError:
        return rejected(reason_code="public-key-encoding")
    try:
        signature = decode_canonical_base64(
            text=required_crypto_corpus_text(payload=payload, field="signatureBase64"),
            exact_octets=64,
        )
    except Base64LengthError:
        return rejected(reason_code="signature-length")
    except NonCanonicalBase64Error:
        return rejected(reason_code="signature-encoding-noncanonical")
    except Base64EncodingError:
        return rejected(reason_code="signature-encoding")
    message = lowercase_hex_bytes(
        text=required_crypto_corpus_text(payload=payload, field="messageHex"),
        allow_empty=True,
    )
    try:
        verify_ed25519_signature(
            public_key,
            signature,
            message,
            context="package-integrity crypto corpus",
        )
    except Ed25519ScalarEncodingError:
        return rejected(reason_code="signature-scalar-noncanonical")
    except Ed25519SignatureEncodingError:
        return rejected(reason_code="point-encoding-invalid")
    except Ed25519SignatureError:
        observation = observe_ed25519_acceptance(
            public_key=bytes.fromhex(public_key_hex),
            message=message,
            signature=signature,
        )
        if observation.cofactored_equation and not observation.uncofactored_equation:
            return rejected(reason_code="signature-equation-invalid")
        return rejected(reason_code="signature-invalid")
    return accepted()


def _observe_public_key(
    *,
    payload: Mapping[str, object],
) -> CryptoCaseObservation:
    key_text = required_crypto_corpus_text(payload=payload, field="publicKeyHex")
    try:
        parse_ed25519_public_key_hex(key_text)
    except Ed25519PointEncodingError:
        return rejected(reason_code="point-encoding-invalid")
    except Ed25519PointOrderError:
        return rejected(reason_code="public-key-order-invalid")
    except Ed25519KeyError:
        if len(key_text) != 64:
            return rejected(reason_code="public-key-length")
        return rejected(reason_code="public-key-encoding")
    return accepted()


def _observe_signature_base64(
    *,
    payload: Mapping[str, object],
) -> CryptoCaseObservation:
    try:
        decoded = decode_canonical_base64(
            text=required_crypto_corpus_text(payload=payload, field="signatureBase64"),
            exact_octets=64,
        )
    except Base64LengthError:
        return rejected(reason_code="signature-length")
    except NonCanonicalBase64Error:
        return rejected(reason_code="signature-encoding-noncanonical")
    except Base64EncodingError:
        return rejected(reason_code="signature-encoding")
    return accepted(decoded_hex=decoded.hex())


__all__ = ["observe_ed25519_operation"]
