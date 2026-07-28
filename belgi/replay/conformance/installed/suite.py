"""Installed normative corpora and non-normative implementation checks."""

from __future__ import annotations

from typing import Protocol

from belgi.carrier.json_representation.conformance.corpus import (
    run_builtin_json_representation_corpus,
)
from belgi.profile.companions.json_representation.selection import (
    DIRECTORY_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER,
    ZIP_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER,
)
from belgi.profile.companions.package_integrity_anchor.conformance.corpus import (
    run_builtin_package_integrity_crypto_corpus,
)
from belgi.replay.package_representation.conformance.corpus import (
    run_builtin_replay_package_representation_corpus,
)
from belgi.replay.package_representation.installed import (
    installed_package_representation_binding,
)
from belgi.replay.reference_profile.finite_evaluator.conformance.corpus import (
    FiniteEvaluatorCheckReport,
    run_builtin_software_change_finite_evaluator_check,
)

from ..exceptions import InstalledConformanceError
from .model import (
    ImplementationCheckResult,
    InstalledConformanceSuite,
    NormativeCorpusResult,
)

__all__ = ["run_installed_conformance_suite"]

_SCHEMA_VERSION = "belgi-installed-conformance-v1"


class _NormativeCorpusReport(Protocol):
    @property
    def corpus_uri(self) -> str: ...

    @property
    def corpus_sha256(self) -> str: ...

    @property
    def schema_version(self) -> str: ...

    @property
    def source_case_count(self) -> int: ...

    @property
    def executed_case_count(self) -> int: ...

    @property
    def observed_rejection_count(self) -> int: ...

    @property
    def mismatched_case_ids(self) -> tuple[str, ...]: ...


def run_installed_conformance_suite() -> InstalledConformanceSuite:
    try:
        json_report = run_builtin_json_representation_corpus()
        directory_binding = installed_package_representation_binding(
            procedure_identifier=(DIRECTORY_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER)
        )
        zip_binding = installed_package_representation_binding(
            procedure_identifier=ZIP_PACKAGE_REPRESENTATION_PROCEDURE_IDENTIFIER
        )
        package_report = run_builtin_replay_package_representation_corpus(
            directory_binding=directory_binding,
            zip_binding=zip_binding,
        )
        integrity_report = run_builtin_package_integrity_crypto_corpus()
        finite_report = run_builtin_software_change_finite_evaluator_check()
    except (OSError, ValueError) as exc:
        raise InstalledConformanceError(
            "The installed exact conformance surface could not be executed."
        ) from exc

    return InstalledConformanceSuite(
        schema_version=_SCHEMA_VERSION,
        normative_corpora=(
            _normative_result(role="json-representation", report=json_report),
            _normative_result(
                role="replay-package-representation",
                report=package_report,
            ),
            _normative_result(
                role="package-integrity-crypto",
                report=integrity_report,
            ),
        ),
        implementation_checks=(_finite_evaluator_check_result(report=finite_report),),
    )


def _normative_result(
    *,
    role: str,
    report: _NormativeCorpusReport,
) -> NormativeCorpusResult:
    return NormativeCorpusResult(
        role=role,
        corpus_uri=report.corpus_uri,
        corpus_sha256=report.corpus_sha256,
        schema_version=report.schema_version,
        source_case_count=report.source_case_count,
        executed_case_count=report.executed_case_count,
        observed_rejection_count=report.observed_rejection_count,
        mismatched_case_ids=report.mismatched_case_ids,
    )


def _finite_evaluator_check_result(
    *,
    report: FiniteEvaluatorCheckReport,
) -> ImplementationCheckResult:
    return ImplementationCheckResult(
        check_id="software-change-finite-reference-validation",
        classification=report.classification,
        scope="finite-reference-validation",
        corpus_identifier=report.corpus_uri,
        corpus_version=report.corpus_version,
        procedure_identifier=report.procedure_identifier,
        procedure_version=report.procedure_version,
        source_case_count=report.source_case_count,
        executed_case_count=report.executed_case_count,
        problem_case_ids=report.mismatched_case_ids,
    )
