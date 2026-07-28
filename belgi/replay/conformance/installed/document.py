"""JSON projection for the installed conformance command."""

from __future__ import annotations

from .model import (
    ImplementationCheckResult,
    InstalledConformanceSuite,
    NormativeCorpusResult,
)

__all__ = ["installed_conformance_to_json_object"]


def installed_conformance_to_json_object(
    *,
    suite: InstalledConformanceSuite,
) -> dict[str, object]:
    return {
        "implementation_checks": [
            _implementation_check_to_json_object(result)
            for result in suite.implementation_checks
        ],
        "normative_corpora": [
            _normative_corpus_to_json_object(result)
            for result in suite.normative_corpora
        ],
        "schema_version": suite.schema_version,
        "status": "passed" if suite.successful else "failed",
        "successful": suite.successful,
    }


def _normative_corpus_to_json_object(
    result: NormativeCorpusResult,
) -> dict[str, object]:
    return {
        "corpus_sha256": result.corpus_sha256,
        "corpus_uri": result.corpus_uri,
        "executed_case_count": result.executed_case_count,
        "mismatch_count": result.mismatch_count,
        "mismatched_case_ids": list(result.mismatched_case_ids),
        "observed_rejection_count": result.observed_rejection_count,
        "role": result.role,
        "schema_version": result.schema_version,
        "source_case_count": result.source_case_count,
        "successful": result.successful,
    }


def _implementation_check_to_json_object(
    result: ImplementationCheckResult,
) -> dict[str, object]:
    return {
        "check_id": result.check_id,
        "classification": result.classification,
        "corpus_identifier": result.corpus_identifier,
        "corpus_version": result.corpus_version,
        "executed_case_count": result.executed_case_count,
        "problem_case_ids": list(result.problem_case_ids),
        "problem_count": result.problem_count,
        "procedure_identifier": result.procedure_identifier,
        "procedure_version": result.procedure_version,
        "scope": result.scope,
        "source_case_count": result.source_case_count,
        "successful": result.successful,
    }
