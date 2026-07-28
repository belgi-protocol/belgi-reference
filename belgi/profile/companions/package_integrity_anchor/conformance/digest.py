from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.companions.package_integrity_anchor.exceptions import (
    SourceDigestMismatchError,
    SourceDigestTextError,
    SourceIdentifierMismatchError,
)
from belgi.profile.companions.package_integrity_anchor.source_binding import (
    require_identified_exact_source,
)
from belgi.substrate.hash import sha256_bytes
from belgi.substrate.hex import decode_lowercase_hex

from .inputs import lowercase_hex_bytes, required_crypto_corpus_text
from .model import CryptoCaseObservation, accepted, rejected


def observe_digest_operation(
    *,
    operation: str,
    payload: Mapping[str, object],
) -> CryptoCaseObservation:
    if operation == "sha256-compute":
        message = lowercase_hex_bytes(
            text=required_crypto_corpus_text(payload=payload, field="messageHex"),
            allow_empty=True,
        )
        return accepted(digest_hex=sha256_bytes(message))
    if operation == "sha256-compare":
        message = lowercase_hex_bytes(
            text=required_crypto_corpus_text(payload=payload, field="messageHex"),
            allow_empty=True,
        )
        digest_hex = required_crypto_corpus_text(payload=payload, field="digestHex")
        try:
            decode_lowercase_hex(text=digest_hex, exact_octets=32)
        except ValueError:
            return rejected(reason_code="digest-text-malformed")
        if sha256_bytes(message) != digest_hex:
            return rejected(reason_code="digest-mismatch")
        return accepted()
    if operation == "sha256-text-validate":
        digest_hex = required_crypto_corpus_text(payload=payload, field="digestHex")
        try:
            decode_lowercase_hex(text=digest_hex, exact_octets=32)
        except ValueError:
            return rejected(reason_code="digest-text-malformed")
        return accepted()
    if operation == "source-binding-validate":
        return _observe_source_binding(payload=payload)
    raise ValueError(f"Unsupported digest corpus operation: {operation!r}.")


def _observe_source_binding(
    *,
    payload: Mapping[str, object],
) -> CryptoCaseObservation:
    source_uri = required_crypto_corpus_text(payload=payload, field="sourceUri")
    digest_hex = required_crypto_corpus_text(payload=payload, field="digestHex")
    source_bytes = lowercase_hex_bytes(
        text=required_crypto_corpus_text(payload=payload, field="sourceBytesHex"),
        allow_empty=True,
    )
    try:
        require_identified_exact_source(
            requested_identifier=required_crypto_corpus_text(
                payload=payload,
                field="requestedIdentifier",
            ),
            designated_identifier=required_crypto_corpus_text(
                payload=payload,
                field="designatedIdentifier",
            ),
            source_uri=source_uri,
            source_bytes=source_bytes,
            digest_algorithm_id=required_crypto_corpus_text(
                payload=payload,
                field="digestAlgorithmId",
            ),
            digest_hex=digest_hex,
        )
    except SourceIdentifierMismatchError:
        return rejected(reason_code="identifier-designator-mismatch")
    except SourceDigestTextError:
        return rejected(reason_code="digest-text-malformed")
    except SourceDigestMismatchError:
        if sha256_bytes(source_uri.encode("utf-8")) == digest_hex:
            return rejected(reason_code="source-binding-uri-text-hash")
        return rejected(reason_code="source-binding-wrong-bytes")
    return accepted()


__all__ = ["observe_digest_operation"]
