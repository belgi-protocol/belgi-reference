from __future__ import annotations

from belgi.profile.governance import (
    ConditionId,
    EnvironmentTermId,
    EvaluatorParameterId,
    EvidenceKindId,
    EvidenceSourceClassId,
)

__all__ = [
    "ACCEPTED_DECISION_VALUE_PARAMETER",
    "AGENT_DECISION_ACCEPTED",
    "AGENT_DECISION_RECORD",
    "AGENT_MODEL_IDENTITY",
    "AGENT_OUTPUT_RECORD",
    "AGENT_POLICY_IDENTITY",
    "AGENT_POLICY_RECORD",
    "AGENT_PROMPT_TEMPLATE_IDENTITY",
    "AGENT_TOOL_SET_IDENTITY",
    "AGENT_TOOL_TRACE",
    "AGENT_TOOL_USE_RECORDED",
    "AGENT_TOOL_USE_SUMMARY",
    "ALL_CONDITIONS",
    "ALL_ENVIRONMENT_TERMS",
    "ALL_EVIDENCE_KINDS",
    "ALL_PARAMETER_IDS",
    "ALL_SOURCE_MATERIAL_ROLES",
    "REQUIRE_TOOL_USE_SUMMARY_PARAMETER",
]


AGENT_DECISION_ACCEPTED = ConditionId(
    "belgi.agent-admission.condition.agent-decision-accepted"
)
AGENT_TOOL_USE_RECORDED = ConditionId(
    "belgi.agent-admission.condition.tool-use-recorded"
)

ALL_CONDITIONS: tuple[ConditionId, ...] = (
    AGENT_DECISION_ACCEPTED,
    AGENT_TOOL_USE_RECORDED,
)

AGENT_DECISION_RECORD = EvidenceKindId(
    "belgi.agent-admission.evidence.agent-decision-record"
)
AGENT_TOOL_USE_SUMMARY = EvidenceKindId(
    "belgi.agent-admission.evidence.tool-use-summary"
)

ALL_EVIDENCE_KINDS: tuple[EvidenceKindId, ...] = (
    AGENT_DECISION_RECORD,
    AGENT_TOOL_USE_SUMMARY,
)

AGENT_OUTPUT_RECORD = EvidenceSourceClassId(
    "belgi.agent-admission.source.agent-output-record"
)
AGENT_TOOL_TRACE = EvidenceSourceClassId(
    "belgi.agent-admission.source.tool-trace-record"
)
AGENT_POLICY_RECORD = EvidenceSourceClassId(
    "belgi.agent-admission.source.policy-record"
)

ALL_SOURCE_MATERIAL_ROLES: tuple[EvidenceSourceClassId, ...] = (
    AGENT_OUTPUT_RECORD,
    AGENT_TOOL_TRACE,
    AGENT_POLICY_RECORD,
)

AGENT_MODEL_IDENTITY = EnvironmentTermId(
    "belgi.agent-admission.environment.agent-model-identity"
)
AGENT_POLICY_IDENTITY = EnvironmentTermId(
    "belgi.agent-admission.environment.agent-policy-identity"
)
AGENT_TOOL_SET_IDENTITY = EnvironmentTermId(
    "belgi.agent-admission.environment.agent-tool-set-identity"
)
AGENT_PROMPT_TEMPLATE_IDENTITY = EnvironmentTermId(
    "belgi.agent-admission.environment.agent-prompt-template-identity"
)

ALL_ENVIRONMENT_TERMS: tuple[EnvironmentTermId, ...] = (
    AGENT_MODEL_IDENTITY,
    AGENT_POLICY_IDENTITY,
    AGENT_TOOL_SET_IDENTITY,
    AGENT_PROMPT_TEMPLATE_IDENTITY,
)

ACCEPTED_DECISION_VALUE_PARAMETER = EvaluatorParameterId(
    "belgi.agent-admission.parameter.accepted-decision-value"
)
REQUIRE_TOOL_USE_SUMMARY_PARAMETER = EvaluatorParameterId(
    "belgi.agent-admission.parameter.require-tool-use-summary"
)

ALL_PARAMETER_IDS: tuple[EvaluatorParameterId, ...] = (
    ACCEPTED_DECISION_VALUE_PARAMETER,
    REQUIRE_TOOL_USE_SUMMARY_PARAMETER,
)
