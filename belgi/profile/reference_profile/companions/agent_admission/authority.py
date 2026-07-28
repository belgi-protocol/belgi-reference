from __future__ import annotations

from collections.abc import Mapping

from belgi.profile.companions.agent_admission.identifiers import (
    AGENT_MODEL_IDENTITY,
    AGENT_OUTPUT_RECORD,
    AGENT_POLICY_IDENTITY,
    AGENT_TOOL_SET_IDENTITY,
    AGENT_TOOL_TRACE,
)

__all__ = [
    "agent_admission_companion_authoritative_subject_supported",
]


def agent_admission_companion_authoritative_subject_supported(
    *,
    item: object,
    source_class: str | None,
) -> bool:
    subject = _agent_admission_subject_from_item(item=item)
    if subject is None:
        return False
    if source_class == str(AGENT_OUTPUT_RECORD):
        return _agent_admission_output_record_supported(subject=subject)
    if source_class == str(AGENT_TOOL_TRACE):
        return _agent_admission_tool_trace_supported(subject=subject)
    return False


def _agent_admission_output_record_supported(
    *,
    subject: Mapping[str, object],
) -> bool:
    return (
        _agent_admission_any_identity_present(
            subject,
            str(AGENT_MODEL_IDENTITY),
            "agent_model_identity",
            "agentModelIdentity",
            "model_identity",
            "modelIdentity",
        )
        and _agent_admission_any_identity_present(
            subject,
            str(AGENT_POLICY_IDENTITY),
            "agent_policy_identity",
            "agentPolicyIdentity",
            "policy_identity",
            "policyIdentity",
        )
        and _agent_admission_any_field_present(
            subject,
            "agent_decision_id",
            "agentDecisionId",
            "decision_identifier",
            "decisionIdentifier",
            "decision_id",
            "decisionId",
            "record_identifier",
            "recordIdentifier",
        )
        and _agent_admission_decision_value_present(subject=subject)
    )


def _agent_admission_tool_trace_supported(
    *,
    subject: Mapping[str, object],
) -> bool:
    return (
        _agent_admission_any_identity_present(
            subject,
            str(AGENT_TOOL_SET_IDENTITY),
            "agent_tool_set_identity",
            "agentToolSetIdentity",
            "tool_set_identity",
            "toolSetIdentity",
        )
        and _agent_admission_any_field_present(
            subject,
            "tool_trace_id",
            "toolTraceId",
            "tool_use_summary_id",
            "toolUseSummaryId",
            "summary_identifier",
            "summaryIdentifier",
            "record_identifier",
            "recordIdentifier",
        )
        and _agent_admission_tool_fact_present(subject=subject)
    )


def _agent_admission_subject_from_item(
    *,
    item: object,
) -> Mapping[str, object] | None:
    subject = getattr(item, "subject", None)
    return _agent_admission_mapping_view(value=subject)


def _agent_admission_mapping_view(
    *,
    value: object,
) -> Mapping[str, object] | None:
    if isinstance(value, Mapping):
        return value
    if not isinstance(value, tuple):
        return None
    mapping: dict[str, object] = {}
    for entry in value:
        if not isinstance(entry, tuple) or len(entry) != 2:
            return None
        key, member = entry
        if not isinstance(key, str):
            return None
        mapping[key] = member
    return mapping


def _agent_admission_any_identity_present(
    subject: Mapping[str, object],
    *keys: str,
) -> bool:
    return any(
        _agent_admission_identity_present(value=value)
        for value in _agent_admission_subject_values(subject, *keys)
    )


def _agent_admission_any_field_present(
    subject: Mapping[str, object],
    *keys: str,
) -> bool:
    return any(
        _agent_admission_field_present(value=value)
        for value in _agent_admission_subject_values(subject, *keys)
    )


def _agent_admission_subject_values(
    subject: Mapping[str, object],
    *keys: str,
) -> tuple[object, ...]:
    values: list[object] = []
    for key in keys:
        if key in subject:
            values.append(subject[key])
    environment = _agent_admission_mapping_view(value=subject.get("environment_terms"))
    if environment is not None:
        for key in keys:
            if key in environment:
                values.append(environment[key])
    return tuple(values)


def _agent_admission_identity_present(*, value: object) -> bool:
    mapping = _agent_admission_mapping_view(value=value)
    if mapping is None:
        return False
    designator = _agent_admission_mapping_view(
        value=(
            mapping.get("immutableDesignator")
            if "immutableDesignator" in mapping
            else mapping.get("immutable_designator")
        )
    )
    if designator is None:
        designator = mapping
    return _agent_admission_immutable_designator_present(designator=designator)


def _agent_admission_immutable_designator_present(
    *,
    designator: Mapping[str, object],
) -> bool:
    uri = _agent_admission_text_member(designator, "uri")
    digest = _agent_admission_mapping_view(value=designator.get("digest"))
    if digest is None:
        digest = designator
    algorithm_id = _agent_admission_text_member(
        digest,
        "algorithmId",
        "algorithm_id",
    )
    digest_value = _agent_admission_text_member(
        digest,
        "digestValue",
        "digest_value",
    )
    return uri is not None and algorithm_id is not None and digest_value is not None


def _agent_admission_text_member(
    mapping: Mapping[str, object],
    *keys: str,
) -> str | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and bool(value.strip()):
            return value
    return None


def _agent_admission_field_present(*, value: object) -> bool:
    if isinstance(value, str) and bool(value.strip()):
        return True
    return isinstance(value, int) and not isinstance(value, bool)


def _agent_admission_decision_value_present(
    *,
    subject: Mapping[str, object],
) -> bool:
    for key in ("decision", "decision_value", "decisionValue", "outcome", "status"):
        value = subject.get(key)
        if isinstance(value, str) and bool(value.strip()):
            return True
        if isinstance(value, bool):
            return True
    return False


def _agent_admission_tool_fact_present(
    *,
    subject: Mapping[str, object],
) -> bool:
    for key in (
        "tool_calls",
        "toolCalls",
        "tool_results",
        "toolResults",
        "tools",
        "tool_names",
        "toolNames",
    ):
        value = subject.get(key)
        if isinstance(value, tuple) and value:
            return True
        if isinstance(value, list) and value:
            return True
        if isinstance(value, str) and bool(value.strip()):
            return True
    return False
