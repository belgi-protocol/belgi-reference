from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.companions.package_integrity_anchor.exceptions import (
    DeprecatedPackageIntegrityMethodError,
    VerificationMethodSourceMismatchError,
)
from belgi.profile.companions.package_integrity_anchor.surface import (
    SupportedPackageIntegritySurface,
    select_package_integrity_surface,
)

from .digest import observe_digest_operation
from .ed25519 import observe_ed25519_operation
from .inputs import required_crypto_corpus_text
from .model import CryptoCaseObservation, rejected

_DIGEST_OPERATIONS = frozenset(
    {
        "sha256-compute",
        "sha256-compare",
        "sha256-text-validate",
        "source-binding-validate",
    }
)
_ED25519_OPERATIONS = frozenset(
    {
        "ed25519-verify",
        "public-key-validate",
        "signature-base64-validate",
    }
)


def execute_package_integrity_crypto_case(
    *,
    case: Mapping[str, object],
    supported_surface: SupportedPackageIntegritySurface,
) -> CryptoCaseObservation:
    operation = required_crypto_corpus_text(payload=case, field="operation")
    raw_input = case.get("input")
    if not isinstance(raw_input, dict):
        raise ValueError("Crypto corpus case input must be an object.")
    if operation in _DIGEST_OPERATIONS:
        return observe_digest_operation(operation=operation, payload=raw_input)
    if operation in _ED25519_OPERATIONS:
        return observe_ed25519_operation(operation=operation, payload=raw_input)
    if operation == "verification-method-select":
        return _observe_selection(
            payload=raw_input,
            supported_surface=supported_surface,
        )
    raise ValueError(f"Unknown package-integrity crypto operation: {operation!r}.")


def _observe_selection(
    *,
    payload: Mapping[str, object],
    supported_surface: SupportedPackageIntegritySurface,
) -> CryptoCaseObservation:
    try:
        select_package_integrity_surface(
            requested_verification_method=required_crypto_corpus_text(
                payload=payload,
                field="requestedVerificationMethod",
            ),
            requested_verification_method_source_uri=_optional_crypto_corpus_text(
                payload=payload,
                field="verificationMethodSourceUri",
            ),
            requested_signature_algorithm=required_crypto_corpus_text(
                payload=payload,
                field="requestedSignatureAlgorithm",
            ),
            requested_signature_algorithm_source_uri=_optional_crypto_corpus_text(
                payload=payload,
                field="signatureAlgorithmSourceUri",
            ),
            supported_surface=supported_surface,
        )
    except DeprecatedPackageIntegrityMethodError:
        return rejected(reason_code="verification-method-deprecated-for-new-use")
    except VerificationMethodSourceMismatchError:
        return rejected(reason_code="verification-method-source-mismatch")
    except ValueError:
        return rejected(reason_code="unsupported-no-fallback")
    return CryptoCaseObservation(result="accepted")


def _optional_crypto_corpus_text(*, payload: Mapping[str, object], field: str) -> str:
    value = payload.get(field, "")
    if not isinstance(value, str):
        raise ValueError(f"Crypto corpus field {field!r} must be text when present.")
    return value


__all__ = ["execute_package_integrity_crypto_case"]
