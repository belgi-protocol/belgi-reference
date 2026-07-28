from __future__ import annotations

from belgi.substrate.hash import sha256_bytes
from belgi.substrate.io import decode_strict_json
from belgi.substrate.resource import load_packaged_bytes

from .cases import (
    json_representation_observation_document,
    observe_json_representation_case,
)
from .inputs import required_json_representation_corpus_text
from .model import JSONRepresentationCorpusReport

JSON_REPRESENTATION_CORPUS_SHA256 = (
    "4aa0fb17037b30a775cf208b52274ac29ad9d03c766f3bf67b5aa79192338366"
)
JSON_REPRESENTATION_CORPUS_URI = (
    "https://belgi.dev/specs/spec-0.5/"
    f"sha256-{JSON_REPRESENTATION_CORPUS_SHA256}/JSONRepresentation.v2.json"
)


def execute_json_representation_corpus(
    *,
    corpus_bytes: bytes,
    corpus_uri: str,
) -> JSONRepresentationCorpusReport:
    observed_sha256 = sha256_bytes(corpus_bytes)
    if (
        corpus_uri == JSON_REPRESENTATION_CORPUS_URI
        and observed_sha256 != JSON_REPRESENTATION_CORPUS_SHA256
    ):
        raise ValueError(
            "The reserved JSON representation corpus URI requires its exact bytes."
        )
    document = decode_strict_json(corpus_bytes, maximum_depth=128)
    if not isinstance(document, dict):
        raise ValueError("JSON representation corpus must be an object.")
    schema_version = required_json_representation_corpus_text(
        document, field="schemaVersion"
    )
    raw_cases = document.get("cases")
    if not isinstance(raw_cases, list):
        raise ValueError("JSON representation corpus cases must be an array.")
    mismatches: list[str] = []
    rejection_count = 0
    executed_count = 0
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            raise ValueError("JSON representation corpus case must be an object.")
        case_id = required_json_representation_corpus_text(raw_case, field="caseId")
        expected = raw_case.get("expected")
        if not isinstance(expected, dict):
            raise ValueError("JSON representation expected result must be an object.")
        outcome = observe_json_representation_case(case=raw_case)
        executed_count += 1
        if not outcome.accepted:
            rejection_count += 1
        if json_representation_observation_document(outcome=outcome) != expected:
            mismatches.append(case_id)
    return JSONRepresentationCorpusReport(
        corpus_uri=_require_json_representation_corpus_uri(corpus_uri),
        corpus_sha256=observed_sha256,
        schema_version=schema_version,
        source_case_count=len(raw_cases),
        executed_case_count=executed_count,
        observed_rejection_count=rejection_count,
        mismatched_case_ids=tuple(mismatches),
    )


def run_builtin_json_representation_corpus() -> JSONRepresentationCorpusReport:
    corpus_bytes = load_packaged_bytes(
        package_name="belgi.carrier.json_representation.conformance",
        path_parts=("data", "JSONRepresentation.v2.json"),
        label="exact JSON representation conformance corpus",
    )
    _require_exact_corpus_digest(corpus_bytes)
    return execute_json_representation_corpus(
        corpus_bytes=corpus_bytes,
        corpus_uri=JSON_REPRESENTATION_CORPUS_URI,
    )


def _require_exact_corpus_digest(corpus_bytes: bytes) -> None:
    observed = sha256_bytes(corpus_bytes)
    if observed != JSON_REPRESENTATION_CORPUS_SHA256:
        raise ValueError(
            "Packaged JSON representation corpus digest mismatch: "
            f"expected {JSON_REPRESENTATION_CORPUS_SHA256}, observed {observed}."
        )


def _require_json_representation_corpus_uri(corpus_uri: str) -> str:
    if corpus_uri == "" or corpus_uri.strip() != corpus_uri:
        raise ValueError("JSON representation corpus URI must be exact non-empty text.")
    return corpus_uri


__all__ = [
    "JSON_REPRESENTATION_CORPUS_SHA256",
    "JSON_REPRESENTATION_CORPUS_URI",
    "execute_json_representation_corpus",
    "run_builtin_json_representation_corpus",
]
