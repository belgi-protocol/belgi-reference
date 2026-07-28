from __future__ import annotations

from belgi.substrate.io import JSONDomainError, canonicalize_jcs, decode_strict_json
from belgi.substrate.schema.exceptions import SchemaGraphError
from belgi.substrate.schema.model import SchemaIssue

from .model import JSONRepresentationOutcome
from .roles import TrustedJSONRole
from .schemas import CarrierSchemaGraph


def _schema_result_code(issues: list[SchemaIssue]) -> str:
    if not issues:
        return "schema-validation-failed"
    if any(issue.keyword == "const" and issue.path == "$.kind" for issue in issues):
        return "trusted-role-schema-mismatch"
    keywords = {issue.keyword for issue in issues}
    for keyword, result_code in (
        ("type", "wrong-json-type"),
        ("format", "format-assertion"),
        ("required", "missing-required-property"),
        ("dependentRequired", "missing-required-property"),
        ("additionalProperties", "additional-property"),
        ("not", "prohibited-property"),
    ):
        if keyword in keywords:
            return result_code
    return "schema-validation-failed"


def validate_json_representation(raw: str | bytes) -> JSONRepresentationOutcome:
    """Validate only the bounded JSON text and value domain."""

    try:
        value = decode_strict_json(raw, maximum_depth=128)
    except JSONDomainError as exc:
        return JSONRepresentationOutcome(
            accepted=False,
            stage=exc.stage,
            result_code=exc.code,
        )
    return JSONRepresentationOutcome(
        accepted=True,
        stage="complete",
        result_code="accepted",
        value=value,
    )


def validate_carrier_json(
    raw: str | bytes,
    *,
    trusted_role: TrustedJSONRole | str,
    canonicalize: bool = False,
    schema_graph: CarrierSchemaGraph | None = None,
) -> JSONRepresentationOutcome:
    """Validate strict JSON under one independently supplied carrier role."""

    domain_outcome = validate_json_representation(raw)
    if not domain_outcome.accepted:
        return domain_outcome
    try:
        role = TrustedJSONRole(trusted_role)
    except ValueError:
        return JSONRepresentationOutcome(
            accepted=False,
            stage="schema",
            result_code="unknown-trusted-role",
        )
    try:
        graph = (
            schema_graph
            if schema_graph is not None
            else CarrierSchemaGraph.from_package()
        )
        issues = graph.validate(
            instance=domain_outcome.value,
            trusted_role=role,
            path="$",
        )
    except SchemaGraphError:
        return JSONRepresentationOutcome(
            accepted=False,
            stage="schema",
            result_code="unresolved-schema-dependency",
        )
    if issues:
        return JSONRepresentationOutcome(
            accepted=False,
            stage="schema",
            result_code=_schema_result_code(issues),
            schema_issues=tuple(issues),
        )
    canonical_bytes = None
    if canonicalize:
        try:
            canonical_bytes = canonicalize_jcs(domain_outcome.value)
        except ValueError:
            return JSONRepresentationOutcome(
                accepted=False,
                stage="json-domain",
                result_code="canonicalization-failure",
            )
    return JSONRepresentationOutcome(
        accepted=True,
        stage="complete",
        result_code="accepted",
        value=domain_outcome.value,
        canonical_bytes=canonical_bytes,
    )


__all__ = ["validate_carrier_json", "validate_json_representation"]
