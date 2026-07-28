"""Bounded support statements for reference-profile companion adoption."""

from __future__ import annotations

from collections.abc import Callable

from belgi.profile.companions.agent_admission.edition import (
    COMPANION_IDENTIFIER as AGENT_IDENTIFIER,
)
from belgi.profile.companions.agent_admission.edition import (
    COMPANION_TITLE as AGENT_TITLE,
)
from belgi.profile.companions.agent_admission.identifiers import (
    AGENT_DECISION_ACCEPTED,
    AGENT_DECISION_RECORD,
    AGENT_MODEL_IDENTITY,
    AGENT_OUTPUT_RECORD,
    AGENT_POLICY_IDENTITY,
    AGENT_TOOL_SET_IDENTITY,
    AGENT_TOOL_TRACE,
    AGENT_TOOL_USE_RECORDED,
    AGENT_TOOL_USE_SUMMARY,
)
from belgi.profile.companions.ci_trust.edition import (
    COMPANION_IDENTIFIER as CI_IDENTIFIER,
)
from belgi.profile.companions.ci_trust.edition import (
    COMPANION_TITLE as CI_TITLE,
)
from belgi.profile.companions.ci_trust.supported import (
    SUPPORTED_CI_ENVIRONMENT_TERMS,
    SUPPORTED_CI_SOURCE_MATERIAL_ROLES,
)
from belgi.profile.companions.python.edition import (
    COMPANION_IDENTIFIER as PYTHON_IDENTIFIER,
)
from belgi.profile.companions.python.edition import (
    COMPANION_TITLE as PYTHON_TITLE,
)
from belgi.profile.companions.python.identifiers.evidence import TEST_REPORT
from belgi.profile.companions.python.identifiers.params import ANALYSIS_SCOPE_PARAMETER
from belgi.profile.companions.python.supported import SUPPORTED_PYTHON_CONDITIONS
from belgi.profile.companions.support import (
    CompanionSupportStatement,
    SupportDirection,
    SupportedIdentifier,
    SupportStatus,
)
from belgi.profile.source_material import ProfileExactEditionSource
from belgi.substrate.time import UtcDate

__all__ = ["build_reference_profile_companion_support_statements"]

_IMPLEMENTATION_IDENTIFIER = "belgi.python-reference-implementation"
_VERIFIER = (SupportDirection.VERIFIER,)


def _entry(*, vocabulary: str, identifier: object) -> SupportedIdentifier:
    return SupportedIdentifier(
        vocabulary=vocabulary,
        identifier=str(identifier),
        directions=_VERIFIER,
    )


def _statement(
    *,
    companion_source: ProfileExactEditionSource,
    document_title: str,
    conformance_class: str,
    status: SupportStatus,
    supported_identifiers: tuple[SupportedIdentifier, ...],
    statement_date: UtcDate,
) -> CompanionSupportStatement:
    return CompanionSupportStatement(
        implementation_identifier=_IMPLEMENTATION_IDENTIFIER,
        document_title=document_title,
        conformance_class=conformance_class,
        status=status,
        companion_source=companion_source,
        supported_identifiers=supported_identifiers,
        statement_date=statement_date,
    )


def build_reference_profile_companion_support_statements(
    *,
    statement_date: UtcDate,
    companion_source_for_identifier: Callable[[str], ProfileExactEditionSource],
) -> tuple[CompanionSupportStatement, ...]:
    return (
        _statement(
            companion_source=companion_source_for_identifier(str(AGENT_IDENTIFIER)),
            document_title=AGENT_TITLE,
            conformance_class="BELGI Agent Admission Vocabulary-aware Verifier",
            status=SupportStatus.DIAGNOSTIC,
            supported_identifiers=(
                _entry(vocabulary="condition", identifier=AGENT_DECISION_ACCEPTED),
                _entry(vocabulary="condition", identifier=AGENT_TOOL_USE_RECORDED),
                _entry(vocabulary="evidence-kind", identifier=AGENT_DECISION_RECORD),
                _entry(vocabulary="evidence-kind", identifier=AGENT_TOOL_USE_SUMMARY),
                _entry(
                    vocabulary="source-material-role", identifier=AGENT_OUTPUT_RECORD
                ),
                _entry(vocabulary="source-material-role", identifier=AGENT_TOOL_TRACE),
                _entry(
                    vocabulary="environment-envelope", identifier=AGENT_MODEL_IDENTITY
                ),
                _entry(
                    vocabulary="environment-envelope", identifier=AGENT_POLICY_IDENTITY
                ),
                _entry(
                    vocabulary="environment-envelope",
                    identifier=AGENT_TOOL_SET_IDENTITY,
                ),
            ),
            statement_date=statement_date,
        ),
        _statement(
            companion_source=companion_source_for_identifier(str(PYTHON_IDENTIFIER)),
            document_title=PYTHON_TITLE,
            conformance_class="BELGI Python Condition Vocabulary-aware Verifier",
            status=SupportStatus.CONFORMANCE,
            supported_identifiers=(
                *(
                    _entry(vocabulary="condition", identifier=identifier)
                    for identifier in SUPPORTED_PYTHON_CONDITIONS
                ),
                _entry(vocabulary="evidence-kind", identifier=TEST_REPORT),
                _entry(
                    vocabulary="evaluator-parameter",
                    identifier=ANALYSIS_SCOPE_PARAMETER,
                ),
            ),
            statement_date=statement_date,
        ),
        _statement(
            companion_source=companion_source_for_identifier(str(CI_IDENTIFIER)),
            document_title=CI_TITLE,
            conformance_class="BELGI CI Trust-Boundary Vocabulary-aware Verifier",
            status=SupportStatus.CONFORMANCE,
            supported_identifiers=(
                *(
                    _entry(vocabulary="source-material-role", identifier=identifier)
                    for identifier in SUPPORTED_CI_SOURCE_MATERIAL_ROLES
                ),
                *(
                    _entry(vocabulary="environment-envelope", identifier=identifier)
                    for identifier in SUPPORTED_CI_ENVIRONMENT_TERMS
                ),
            ),
            statement_date=statement_date,
        ),
    )
