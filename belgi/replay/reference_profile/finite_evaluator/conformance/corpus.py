"""Digest-bound execution of SoftwareChangeFiniteEvaluator v1."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from belgi.profile.edition_catalog import exact_edition_document_for_key
from belgi.substrate.hash import sha256_bytes
from belgi.substrate.io import decode_strict_json
from belgi.substrate.resource import load_packaged_bytes

from .execution import observe_finite_evaluator_input
from .mutations import apply_case_mutations

SOFTWARE_CHANGE_FINITE_EVALUATOR_SHA256 = (
    "cc5b46b1c96879be243f58747561ad751b0f8964fa14f0013c42675c019d5ae5"
)
SOFTWARE_CHANGE_FINITE_EVALUATOR_URI = (
    "https://belgi.dev/specs/spec-0.5/"
    f"sha256-{SOFTWARE_CHANGE_FINITE_EVALUATOR_SHA256}/"
    "SoftwareChangeFiniteEvaluator.v1.json"
)
_FINITE_EVALUATOR_CORPUS_SCHEMA_VERSION = (
    "belgi-software-change-finite-evaluator-reference-validation-v1"
)
_FINITE_EVALUATOR_CORPUS_VERSION = "1"
_FINITE_EVALUATOR_PART_VERSION = "0.5"
_FINITE_EVALUATOR_PROCEDURE_ANCHOR = "clause-12.7"
_FINITE_EVALUATOR_PROCEDURE_REQUIREMENT = {
    "requirementId": "P4-FE-004",
    "document": "spec/BELGI-Part-4-Software-Change-Admission-Profile.md",
    "clauseLocator": "Clauses 11.5 and 12.7",
    "heading": "Decisive bindings and total evaluator",
}


@dataclass(frozen=True, slots=True, kw_only=True)
class FiniteEvaluatorCheckReport:
    classification: str
    corpus_uri: str
    corpus_sha256: str
    corpus_version: str
    procedure_identifier: str
    procedure_version: str
    source_case_count: int
    executed_case_count: int
    observed_success_count: int
    observed_lift_failure_count: int
    mismatched_case_ids: tuple[str, ...]

    @property
    def successful(self) -> bool:
        return (
            self.source_case_count == self.executed_case_count
            and not self.mismatched_case_ids
        )


def execute_software_change_finite_evaluator_check(
    *, corpus_bytes: bytes, corpus_uri: str
) -> FiniteEvaluatorCheckReport:
    """Execute all inputs as a non-normative implementation check."""

    observed_digest = sha256_bytes(corpus_bytes)
    if (
        corpus_uri == SOFTWARE_CHANGE_FINITE_EVALUATOR_URI
        and observed_digest != SOFTWARE_CHANGE_FINITE_EVALUATOR_SHA256
    ):
        raise ValueError("reserved finite evaluator corpus URI requires exact bytes.")
    document = decode_strict_json(corpus_bytes, maximum_depth=128)
    if not isinstance(document, dict):
        raise ValueError("finite evaluator corpus must be an object.")
    if document.get("corpusRole") != "finite-reference-validation":
        raise ValueError("finite evaluator corpus identity is unsupported.")
    (
        corpus_version,
        procedure_identifier,
        procedure_version,
    ) = _finite_evaluator_report_identity(corpus_document=document)
    base_input = _finite_corpus_mapping(document.get("baseInput"), label="baseInput")
    cases = document.get("cases")
    if not isinstance(cases, list):
        raise ValueError("finite evaluator corpus cases must be an array.")
    mismatches: list[str] = []
    success_count = 0
    lift_failure_count = 0
    for raw_case in cases:
        case = _finite_corpus_mapping(raw_case, label="case")
        case_id = _finite_corpus_text(case.get("caseId"), label="caseId")
        if case.get("operation") != "finite-logical-evaluate":
            raise ValueError(f"finite evaluator case {case_id!r} operation is invalid.")
        input_document = apply_case_mutations(
            base_input=base_input,
            mutations=case.get("mutations"),
        )
        observed = observe_finite_evaluator_input(input_document=input_document)
        expected = _finite_corpus_mapping(
            case.get("expected"), label=f"{case_id}.expected"
        )
        if observed["resultKind"] == "success":
            success_count += 1
        elif observed["resultKind"] == "lift-failure":
            lift_failure_count += 1
        if observed != expected:
            mismatches.append(case_id)
    return FiniteEvaluatorCheckReport(
        classification="implementation_check",
        corpus_uri=_finite_corpus_text(corpus_uri, label="corpus URI"),
        corpus_sha256=observed_digest,
        corpus_version=corpus_version,
        procedure_identifier=procedure_identifier,
        procedure_version=procedure_version,
        source_case_count=len(cases),
        executed_case_count=len(cases),
        observed_success_count=success_count,
        observed_lift_failure_count=lift_failure_count,
        mismatched_case_ids=tuple(mismatches),
    )


def run_builtin_software_change_finite_evaluator_check() -> FiniteEvaluatorCheckReport:
    corpus_bytes = load_packaged_bytes(
        package_name="belgi.replay.reference_profile.finite_evaluator.conformance",
        path_parts=("data", "SoftwareChangeFiniteEvaluator.v1.json"),
        label="exact SoftwareChangeFiniteEvaluator reference-validation material",
    )
    if sha256_bytes(corpus_bytes) != SOFTWARE_CHANGE_FINITE_EVALUATOR_SHA256:
        raise ValueError("packaged finite evaluator corpus digest mismatch.")
    return execute_software_change_finite_evaluator_check(
        corpus_bytes=corpus_bytes,
        corpus_uri=SOFTWARE_CHANGE_FINITE_EVALUATOR_URI,
    )


def _finite_evaluator_report_identity(
    *, corpus_document: Mapping[str, object]
) -> tuple[str, str, str]:
    if corpus_document.get("schemaVersion") != _FINITE_EVALUATOR_CORPUS_SCHEMA_VERSION:
        raise ValueError("finite evaluator corpus identity is unsupported.")
    part = _finite_corpus_mapping(corpus_document.get("part"), label="part")
    part_version = _finite_corpus_text(
        part.get("versionDesignator"), label="part.versionDesignator"
    )
    if part_version != _FINITE_EVALUATOR_PART_VERSION:
        raise ValueError("finite evaluator Part version is unsupported.")
    requirement_links = corpus_document.get("requirementLinks")
    if not isinstance(requirement_links, list):
        raise ValueError("finite evaluator requirementLinks must be an array.")
    matching_requirements = [
        _finite_corpus_mapping(link, label="requirementLinks item")
        for link in requirement_links
        if isinstance(link, Mapping)
        and link.get("requirementId")
        == _FINITE_EVALUATOR_PROCEDURE_REQUIREMENT["requirementId"]
    ]
    if len(matching_requirements) != 1 or dict(matching_requirements[0]) != (
        _FINITE_EVALUATOR_PROCEDURE_REQUIREMENT
    ):
        raise ValueError(
            "finite evaluator procedure requirement identity is unsupported."
        )
    part4_uri = _require_installed_exact_part4(corpus_document=corpus_document)
    return (
        _FINITE_EVALUATOR_CORPUS_VERSION,
        f"{part4_uri}#{_FINITE_EVALUATOR_PROCEDURE_ANCHOR}",
        part_version,
    )


def _require_installed_exact_part4(*, corpus_document: Mapping[str, object]) -> str:
    source = _finite_corpus_mapping(
        corpus_document.get("exactPart4Source"),
        label="exactPart4Source",
    )
    designator = _finite_corpus_mapping(
        source.get("immutableDesignator"),
        label="exactPart4Source.immutableDesignator",
    )
    digest = _finite_corpus_mapping(
        designator.get("digest"),
        label="exactPart4Source.immutableDesignator.digest",
    )
    expected_uri = _finite_corpus_text(
        designator.get("uri"),
        label="exactPart4Source.immutableDesignator.uri",
    )
    expected_algorithm = _finite_corpus_text(
        digest.get("algorithmId"),
        label="exactPart4Source.immutableDesignator.digest.algorithmId",
    )
    expected_digest = _finite_corpus_text(
        digest.get("digestValue"),
        label="exactPart4Source.immutableDesignator.digest.digestValue",
    )
    document = exact_edition_document_for_key(key="software-change-admission-profile")
    if (
        expected_algorithm != "sha256"
        or document.uri != expected_uri
        or document.sha256 != expected_digest
    ):
        raise ValueError("installed finite evaluator Part 4 source identity mismatch.")
    return expected_uri


def _finite_corpus_mapping(value: object, *, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"finite evaluator corpus {label} must be an object.")
    return value


def _finite_corpus_text(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"finite evaluator corpus {label} must be normalized text.")
    return value
