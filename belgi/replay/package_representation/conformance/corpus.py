from __future__ import annotations

from belgi.carrier.package.representation.binding import PackageRepresentationBinding
from belgi.substrate.hash import sha256_bytes
from belgi.substrate.io import decode_strict_json
from belgi.substrate.resource import load_packaged_bytes

from .cases import (
    observe_replay_package_representation_case,
    require_normative_representation_bindings,
)
from .inputs import required_replay_package_corpus_text
from .model import ReplayPackageRepresentationCorpusReport

REPLAY_PACKAGE_REPRESENTATION_CORPUS_SHA256 = (
    "9808668115f98467ac8ededae94a52184777d33673404bd0076a5982554bdee0"
)
REPLAY_PACKAGE_REPRESENTATION_CORPUS_URI = (
    "https://belgi.dev/specs/spec-0.5/"
    f"sha256-{REPLAY_PACKAGE_REPRESENTATION_CORPUS_SHA256}/"
    "ReplayPackageRepresentation.v3.json"
)


def execute_replay_package_representation_corpus(
    *,
    corpus_bytes: bytes,
    corpus_uri: str,
    directory_binding: PackageRepresentationBinding,
    zip_binding: PackageRepresentationBinding,
) -> ReplayPackageRepresentationCorpusReport:
    observed_sha256 = sha256_bytes(corpus_bytes)
    if (
        corpus_uri == REPLAY_PACKAGE_REPRESENTATION_CORPUS_URI
        and observed_sha256 != REPLAY_PACKAGE_REPRESENTATION_CORPUS_SHA256
    ):
        raise ValueError(
            "The reserved replay-package representation corpus URI requires "
            "its exact bytes."
        )
    require_normative_representation_bindings(
        directory_binding=directory_binding,
        zip_binding=zip_binding,
    )
    document = decode_strict_json(corpus_bytes, maximum_depth=128)
    if not isinstance(document, dict):
        raise ValueError("Replay-package representation corpus must be an object.")
    schema_version = required_replay_package_corpus_text(
        document, field="schemaVersion"
    )
    raw_cases = document.get("cases")
    if not isinstance(raw_cases, list):
        raise ValueError("Replay-package representation cases must be an array.")
    mismatches: list[str] = []
    rejection_count = 0
    executed_count = 0
    for raw_case in raw_cases:
        if not isinstance(raw_case, dict):
            raise ValueError("Replay-package representation case must be an object.")
        case_id = required_replay_package_corpus_text(raw_case, field="caseId")
        expected = raw_case.get("expected")
        if not isinstance(expected, dict):
            raise ValueError("Replay-package expected result must be an object.")
        observed = observe_replay_package_representation_case(
            case=raw_case,
            directory_binding=directory_binding,
            zip_binding=zip_binding,
        )
        executed_count += 1
        if observed.get("accepted") is False:
            rejection_count += 1
        if observed != expected:
            mismatches.append(case_id)
    return ReplayPackageRepresentationCorpusReport(
        corpus_uri=_require_replay_package_representation_corpus_uri(corpus_uri),
        corpus_sha256=observed_sha256,
        schema_version=schema_version,
        source_case_count=len(raw_cases),
        executed_case_count=executed_count,
        observed_rejection_count=rejection_count,
        mismatched_case_ids=tuple(mismatches),
    )


def run_builtin_replay_package_representation_corpus(
    *,
    directory_binding: PackageRepresentationBinding,
    zip_binding: PackageRepresentationBinding,
) -> ReplayPackageRepresentationCorpusReport:
    corpus_bytes = load_packaged_bytes(
        package_name="belgi.replay.package_representation.conformance",
        path_parts=("data", "ReplayPackageRepresentation.v3.json"),
        label="exact replay-package representation conformance corpus",
    )
    observed = sha256_bytes(corpus_bytes)
    if observed != REPLAY_PACKAGE_REPRESENTATION_CORPUS_SHA256:
        raise ValueError(
            "Packaged replay-package representation corpus digest mismatch: "
            f"expected {REPLAY_PACKAGE_REPRESENTATION_CORPUS_SHA256}, "
            f"observed {observed}."
        )
    return execute_replay_package_representation_corpus(
        corpus_bytes=corpus_bytes,
        corpus_uri=REPLAY_PACKAGE_REPRESENTATION_CORPUS_URI,
        directory_binding=directory_binding,
        zip_binding=zip_binding,
    )


def _require_replay_package_representation_corpus_uri(corpus_uri: str) -> str:
    if corpus_uri == "" or corpus_uri.strip() != corpus_uri:
        raise ValueError("Replay-package corpus URI must be exact non-empty text.")
    return corpus_uri


__all__ = [
    "REPLAY_PACKAGE_REPRESENTATION_CORPUS_SHA256",
    "REPLAY_PACKAGE_REPRESENTATION_CORPUS_URI",
    "execute_replay_package_representation_corpus",
    "run_builtin_replay_package_representation_corpus",
]
