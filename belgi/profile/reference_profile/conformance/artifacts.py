from __future__ import annotations

from pathlib import Path

from belgi.profile.edition import (
    Digest,
    ImmutableDesignator,
    external_edition_binding,
)
from belgi.profile.governance import DependencyReference
from belgi.profile.reference_profile.edition_info import PROFILE_VERSION

from .model import ReferenceProfileConformanceArtifactSet

__all__ = [
    "SOFTWARE_CHANGE_REPLAY_REPORT_CORPUS_CLAUSE_LOCATOR",
    "SOFTWARE_CHANGE_REPLAY_REPORT_CORPUS_IDENTIFIER",
    "SOFTWARE_CHANGE_REPLAY_REPORT_CORPUS_SHA256",
    "SOFTWARE_CHANGE_REPLAY_REPORT_CORPUS_URI",
    "SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_CLAUSE_LOCATOR",
    "SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_IDENTIFIER",
    "SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_PATH",
    "SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_SHA256",
    "SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_URI",
    "SOFTWARE_CHANGE_REPLAY_REPORT_PROCEDURE_CLAUSE_LOCATOR",
    "SOFTWARE_CHANGE_REPLAY_REPORT_PROCEDURE_IDENTIFIER",
    "SOFTWARE_CHANGE_REPLAY_REPORT_PROCEDURE_SHA256",
    "SOFTWARE_CHANGE_REPLAY_REPORT_PROCEDURE_URI",
    "VERDICT_INTEROP_CORPUS_CLAUSE_LOCATOR",
    "VERDICT_INTEROP_CORPUS_IDENTIFIER",
    "VERDICT_INTEROP_CORPUS_SHA256",
    "VERDICT_INTEROP_CORPUS_URI",
    "VERDICT_INTEROP_PROCEDURE_CLAUSE_LOCATOR",
    "VERDICT_INTEROP_PROCEDURE_IDENTIFIER",
    "VERDICT_INTEROP_PROCEDURE_SHA256",
    "VERDICT_INTEROP_PROCEDURE_URI",
    "reference_profile_builtin_verdict_interop_artifact_set",
    "reference_profile_software_change_replay_report_corpus_dependency",
    "reference_profile_software_change_replay_report_procedure_dependency",
    "reference_profile_verdict_interop_artifact_set",
    "reference_profile_verdict_interop_corpus_dependency",
    "reference_profile_verdict_interop_procedure_dependency",
]


VERDICT_INTEROP_CORPUS_IDENTIFIER = (
    "urn:belgi:profile:software-change-admission:conformance:"
    "agent-admission-verdict-interop-corpus"
)
VERDICT_INTEROP_PROCEDURE_IDENTIFIER = (
    "urn:belgi:profile:software-change-admission:conformance:"
    "agent-admission-verdict-interop-procedure"
)
SOFTWARE_CHANGE_REPLAY_REPORT_CORPUS_IDENTIFIER = (
    "urn:belgi:profile:software-change-admission:conformance:replay-report-corpus"
)
SOFTWARE_CHANGE_REPLAY_REPORT_PROCEDURE_IDENTIFIER = (
    "urn:belgi:profile:software-change-admission:conformance:replay-report-procedure"
)
SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_IDENTIFIER = (
    "urn:belgi:profile:software-change-admission:conformance:replay-report-declaration"
)
VERDICT_INTEROP_CORPUS_CLAUSE_LOCATOR = (
    "profile.conformance.agent-admission.verdict-interop-corpus"
)
VERDICT_INTEROP_PROCEDURE_CLAUSE_LOCATOR = (
    "profile.conformance.agent-admission.verdict-interop-procedure"
)
SOFTWARE_CHANGE_REPLAY_REPORT_CORPUS_CLAUSE_LOCATOR = (
    "profile.conformance.software-change-admission.replay-report-corpus"
)
SOFTWARE_CHANGE_REPLAY_REPORT_PROCEDURE_CLAUSE_LOCATOR = (
    "profile.conformance.software-change-admission.replay-report-procedure"
)
SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_CLAUSE_LOCATOR = (
    "profile.conformance.software-change-admission.replay-report-declaration"
)
VERDICT_INTEROP_CORPUS_URI = (
    "https://belgi.dev/reference-profile/conformance/"
    "agent-admission-verdict/corpus.json"
)
VERDICT_INTEROP_PROCEDURE_URI = (
    "https://belgi.dev/reference-profile/conformance/"
    "agent-admission-verdict/procedure.json"
)
SOFTWARE_CHANGE_REPLAY_REPORT_CORPUS_URI = (
    "https://belgi.dev/reference-profile/conformance/"
    "software-change-admission-report/corpus.json"
)
SOFTWARE_CHANGE_REPLAY_REPORT_PROCEDURE_URI = (
    "https://belgi.dev/reference-profile/conformance/"
    "software-change-admission-report/procedure.json"
)
SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_URI = (
    "https://belgi.dev/reference-profile/conformance/"
    "software-change-admission-report/declaration.json"
)
VERDICT_INTEROP_CORPUS_SHA256 = (
    "5192c1895d75d3069d1120b558b7a8d959f958e16772c911d2e582e5ce65d2c1"
)
VERDICT_INTEROP_PROCEDURE_SHA256 = (
    "b766c8d4190e7e7e8c65580a67df75f897783f72ef041d2eea290c72dc633d8b"
)
SOFTWARE_CHANGE_REPLAY_REPORT_CORPUS_SHA256 = (
    "c2f479599ee5f8f9884f7eebdc33589e0fbf47d71d975df747cf67fbb682c315"
)
SOFTWARE_CHANGE_REPLAY_REPORT_PROCEDURE_SHA256 = (
    "ee8ed4d0dbf68fdde4a5fbfc9670e1aee00d08125b1b5b26210f67d47799ba1c"
)
SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_SHA256 = (
    "5bdaa9fbbad37ba7796b4157f14713f1a22d3e35709b726f8761abac54b635e5"
)

_SOFTWARE_CHANGE_REPLAY_REPORT_DIRECTORY = "software-change-admission-report"
_SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_FILENAME = "declaration.json"


def _reference_profile_conformance_data_directory() -> Path:
    return Path(__file__).resolve().parent / "data"


SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_PATH = (
    _reference_profile_conformance_data_directory()
    / _SOFTWARE_CHANGE_REPLAY_REPORT_DIRECTORY
    / _SOFTWARE_CHANGE_REPLAY_REPORT_DECLARATION_FILENAME
)


def _reference_profile_conformance_designator(
    *,
    uri: str,
    digest_value: str,
) -> ImmutableDesignator:
    return ImmutableDesignator(
        uri=uri,
        digest=Digest(
            algorithm_id="sha256",
            digest_value=digest_value,
        ),
    )


def _reference_profile_conformance_dependency(
    *,
    identifier: str,
    immutable_designator: ImmutableDesignator,
    clause_locator: str,
) -> DependencyReference:
    return DependencyReference(
        binding=external_edition_binding(
            identifier=identifier,
            version=PROFILE_VERSION,
            immutable_designator=immutable_designator,
        ),
        replay_relevant=True,
        clause_locator=clause_locator,
    )


def reference_profile_verdict_interop_corpus_dependency(
    *,
    immutable_designator: ImmutableDesignator,
) -> DependencyReference:
    return _reference_profile_conformance_dependency(
        identifier=VERDICT_INTEROP_CORPUS_IDENTIFIER,
        immutable_designator=immutable_designator,
        clause_locator=VERDICT_INTEROP_CORPUS_CLAUSE_LOCATOR,
    )


def reference_profile_verdict_interop_procedure_dependency(
    *,
    immutable_designator: ImmutableDesignator,
) -> DependencyReference:
    return _reference_profile_conformance_dependency(
        identifier=VERDICT_INTEROP_PROCEDURE_IDENTIFIER,
        immutable_designator=immutable_designator,
        clause_locator=VERDICT_INTEROP_PROCEDURE_CLAUSE_LOCATOR,
    )


def reference_profile_software_change_replay_report_corpus_dependency(
    *,
    immutable_designator: ImmutableDesignator,
) -> DependencyReference:
    return _reference_profile_conformance_dependency(
        identifier=SOFTWARE_CHANGE_REPLAY_REPORT_CORPUS_IDENTIFIER,
        immutable_designator=immutable_designator,
        clause_locator=SOFTWARE_CHANGE_REPLAY_REPORT_CORPUS_CLAUSE_LOCATOR,
    )


def reference_profile_software_change_replay_report_procedure_dependency(
    *,
    immutable_designator: ImmutableDesignator,
) -> DependencyReference:
    return _reference_profile_conformance_dependency(
        identifier=SOFTWARE_CHANGE_REPLAY_REPORT_PROCEDURE_IDENTIFIER,
        immutable_designator=immutable_designator,
        clause_locator=SOFTWARE_CHANGE_REPLAY_REPORT_PROCEDURE_CLAUSE_LOCATOR,
    )


def reference_profile_verdict_interop_artifact_set(
    *,
    corpus_designator: ImmutableDesignator,
    procedure_designator: ImmutableDesignator,
) -> ReferenceProfileConformanceArtifactSet:
    return ReferenceProfileConformanceArtifactSet(
        verdict_interoperability_corpus=(
            reference_profile_verdict_interop_corpus_dependency(
                immutable_designator=corpus_designator,
            )
        ),
        verdict_interoperability_procedure=(
            reference_profile_verdict_interop_procedure_dependency(
                immutable_designator=procedure_designator,
            )
        ),
    )


def reference_profile_builtin_verdict_interop_artifact_set() -> (
    ReferenceProfileConformanceArtifactSet
):
    return reference_profile_verdict_interop_artifact_set(
        corpus_designator=_reference_profile_conformance_designator(
            uri=VERDICT_INTEROP_CORPUS_URI,
            digest_value=VERDICT_INTEROP_CORPUS_SHA256,
        ),
        procedure_designator=_reference_profile_conformance_designator(
            uri=VERDICT_INTEROP_PROCEDURE_URI,
            digest_value=VERDICT_INTEROP_PROCEDURE_SHA256,
        ),
    )
