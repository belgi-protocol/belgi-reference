from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.companions.package_integrity_anchor.surface import (
    SupportedPackageIntegritySurface,
)
from belgi.substrate.hash import sha256_bytes
from belgi.substrate.io import decode_strict_json
from belgi.substrate.resource import load_packaged_bytes

from .execution import execute_package_integrity_crypto_case
from .inputs import required_crypto_corpus_text
from .surface import built_in_package_integrity_crypto_surface


@dataclass(frozen=True, slots=True, kw_only=True)
class PackageIntegrityCryptoCorpusReport:
    corpus_uri: str
    schema_version: str
    corpus_sha256: str
    source_case_count: int
    executed_case_count: int
    observed_rejection_count: int
    mismatched_case_ids: tuple[str, ...]

    @property
    def mismatch_count(self) -> int:
        return len(self.mismatched_case_ids)

    @property
    def successful(self) -> bool:
        return (
            self.executed_case_count == self.source_case_count
            and not self.mismatched_case_ids
        )


PACKAGE_INTEGRITY_CRYPTO_CORPUS_SHA256 = (
    "0b2467b656f595ff751d5d555438362f8c50660302d3b45c164c07449dd1428c"
)
PACKAGE_INTEGRITY_CRYPTO_CORPUS_URI = (
    "https://belgi.dev/specs/spec-0.4/"
    f"sha256-{PACKAGE_INTEGRITY_CRYPTO_CORPUS_SHA256}/"
    "PackageIntegrityCrypto.v2.json"
)


def execute_package_integrity_crypto_corpus(
    *,
    corpus_bytes: bytes,
    corpus_uri: str,
    supported_surface: SupportedPackageIntegritySurface,
) -> PackageIntegrityCryptoCorpusReport:
    observed_sha256 = sha256_bytes(corpus_bytes)
    if (
        corpus_uri == PACKAGE_INTEGRITY_CRYPTO_CORPUS_URI
        and observed_sha256 != PACKAGE_INTEGRITY_CRYPTO_CORPUS_SHA256
    ):
        raise ValueError(
            "The reserved package-integrity crypto corpus URI requires its exact bytes."
        )
    document = decode_strict_json(corpus_bytes, maximum_depth=128)
    if not isinstance(document, dict):
        raise ValueError("Package-integrity crypto corpus must be an object.")
    schema_version = required_crypto_corpus_text(
        payload=document, field="schemaVersion"
    )
    raw_cases = document.get("cases")
    if not isinstance(raw_cases, list):
        raise ValueError("Package-integrity crypto corpus cases must be an array.")
    mismatches: list[str] = []
    observed_rejections = 0
    executed_count = 0
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            raise ValueError("Package-integrity crypto corpus case must be an object.")
        observation = execute_package_integrity_crypto_case(
            case=raw_case,
            supported_surface=supported_surface,
        )
        executed_count += 1
        if not observation.result == "accepted":
            observed_rejections += 1
        expected = raw_case.get("expected")
        if not isinstance(expected, dict):
            raise ValueError(
                "Package-integrity crypto expected result must be an object."
            )
        if observation.to_json_object() != expected:
            mismatches.append(
                required_crypto_corpus_text(payload=raw_case, field="caseId")
            )
    return PackageIntegrityCryptoCorpusReport(
        corpus_uri=_require_package_integrity_crypto_corpus_uri(corpus_uri),
        schema_version=schema_version,
        corpus_sha256=observed_sha256,
        source_case_count=len(raw_cases),
        executed_case_count=executed_count,
        observed_rejection_count=observed_rejections,
        mismatched_case_ids=tuple(mismatches),
    )


def run_builtin_package_integrity_crypto_corpus() -> PackageIntegrityCryptoCorpusReport:
    corpus_bytes = load_packaged_bytes(
        package_name=("belgi.profile.companions.package_integrity_anchor.conformance"),
        path_parts=("data", "PackageIntegrityCrypto.v2.json"),
        label="exact package-integrity crypto conformance corpus",
    )
    observed = sha256_bytes(corpus_bytes)
    if observed != PACKAGE_INTEGRITY_CRYPTO_CORPUS_SHA256:
        raise ValueError(
            "Packaged package-integrity crypto corpus digest mismatch: "
            f"expected {PACKAGE_INTEGRITY_CRYPTO_CORPUS_SHA256}, observed {observed}."
        )
    return execute_package_integrity_crypto_corpus(
        corpus_bytes=corpus_bytes,
        corpus_uri=PACKAGE_INTEGRITY_CRYPTO_CORPUS_URI,
        supported_surface=built_in_package_integrity_crypto_surface(),
    )


def _require_package_integrity_crypto_corpus_uri(corpus_uri: str) -> str:
    if corpus_uri == "" or corpus_uri.strip() != corpus_uri:
        raise ValueError(
            "Package-integrity crypto corpus URI must be exact non-empty text."
        )
    return corpus_uri


__all__ = [
    "PACKAGE_INTEGRITY_CRYPTO_CORPUS_SHA256",
    "PACKAGE_INTEGRITY_CRYPTO_CORPUS_URI",
    "PackageIntegrityCryptoCorpusReport",
    "execute_package_integrity_crypto_corpus",
    "run_builtin_package_integrity_crypto_corpus",
]
