from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError
from referencing.exceptions import Unresolvable

from belgi.substrate.schema.equality import json_values_equal
from belgi.substrate.schema.exceptions import SchemaGraphError
from belgi.substrate.schema.model import SchemaIssue
from belgi.substrate.schema.reference import LocalSchemaRegistry
from belgi.substrate.schema.scalar import is_absolute_uri
from belgi.substrate.schema.types import json_type_name

_DRAFT_2020_12_URI = "https://json-schema.org/draft/2020-12/schema"


def _issue_path(*, root: str, parts: Iterable[object]) -> str:
    rendered = root
    for part in parts:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def _format_checker() -> FormatChecker:
    checker = FormatChecker()
    checker.checks("uri")(is_absolute_uri)
    return checker


def _schema_branch_suffix(error: ValidationError) -> str:
    schema_path = list(error.absolute_schema_path)
    if "allOf" not in schema_path:
        return ""
    index = schema_path.index("allOf")
    if index + 1 >= len(schema_path) or not isinstance(schema_path[index + 1], int):
        return ""
    return f"(allOf[{schema_path[index + 1]}])"


def _draft_issue_message(error: ValidationError) -> str:
    keyword = error.validator
    if keyword == "additionalProperties":
        return "additionalProperties not allowed"
    if keyword == "required":
        required_names = (
            error.validator_value if isinstance(error.validator_value, list) else []
        )
        missing = next(
            (
                name
                for name in required_names
                if isinstance(name, str)
                and isinstance(error.instance, dict)
                and name not in error.instance
                and error.message.startswith(repr(name))
            ),
            None,
        )
        return f"missing required {missing!r}" if missing is not None else error.message
    if keyword == "type":
        return (
            f"expected type {error.validator_value}, "
            f"got {json_type_name(error.instance)}"
        )
    if keyword == "const":
        return "const mismatch"
    if keyword == "enum":
        return "enum mismatch"
    if keyword == "format":
        return f"invalid {error.validator_value}"
    if keyword == "pattern":
        return "pattern mismatch"
    if keyword == "oneOf":
        count = 0 if error.context else 2
        return f"oneOf match_count={count} (expected exactly 1)"
    if keyword == "anyOf":
        return "anyOf match_count=0 (expected at least 1)"
    if keyword in {
        "maxItems",
        "maxLength",
        "maxProperties",
        "maximum",
        "minItems",
        "minLength",
        "minProperties",
        "minimum",
    }:
        return f"{keyword} {error.validator_value}"
    return error.message


def _additional_property_names(error: ValidationError) -> list[str]:
    if not isinstance(error.instance, dict) or not isinstance(error.schema, dict):
        return []
    declared = error.schema.get("properties", {})
    if not isinstance(declared, dict):
        return []
    return sorted(str(name) for name in error.instance.keys() - declared.keys())


def _unique_item_issues(*, error: ValidationError, path: str) -> list[SchemaIssue]:
    if not isinstance(error.instance, list):
        return []
    issues: list[SchemaIssue] = []
    for index, value in enumerate(error.instance):
        duplicate_of = next(
            (
                prior_index
                for prior_index, prior in enumerate(error.instance[:index])
                if json_values_equal(value, prior)
            ),
            None,
        )
        if duplicate_of is not None:
            issues.append(
                SchemaIssue(
                    path=f"{path}[{index}]",
                    message=f"uniqueItems duplicate of index {duplicate_of}",
                    keyword="uniqueItems",
                )
            )
    return issues


def _draft_issues_for_error(*, error: ValidationError, path: str) -> list[SchemaIssue]:
    issue_path = _issue_path(root=path, parts=error.absolute_path)
    issue_path += _schema_branch_suffix(error)
    if "propertyNames" in error.absolute_schema_path:
        issue_path += "."
    if error.validator == "additionalProperties":
        names = _additional_property_names(error)
        if names:
            return [
                SchemaIssue(
                    path=f"{issue_path}.{name}",
                    message="additionalProperties not allowed",
                    keyword="additionalProperties",
                )
                for name in names
            ]
    if error.validator == "uniqueItems":
        expanded = _unique_item_issues(error=error, path=issue_path)
        if expanded:
            return expanded
    return [
        SchemaIssue(
            path=issue_path,
            message=_draft_issue_message(error),
            keyword=str(error.validator) if error.validator is not None else None,
        )
    ]


def _draft_issues(*, errors: Iterable[ValidationError], path: str) -> list[SchemaIssue]:
    issues = [
        issue
        for error in errors
        for issue in _draft_issues_for_error(error=error, path=path)
    ]
    issues.sort(key=lambda issue: (issue.path, issue.message, issue.keyword or ""))
    return issues


def validate_local_schema(
    *,
    registry: LocalSchemaRegistry,
    instance: object,
    root_uri: str,
    path: str,
) -> list[SchemaIssue]:
    try:
        root_schema = registry.schemas_by_uri[root_uri]
    except KeyError as exc:
        raise SchemaGraphError(
            f"selected root schema is unavailable: {root_uri}"
        ) from exc
    expected_dialect = (
        _DRAFT_2020_12_URI if root_uri == registry.dialect_uri else registry.dialect_uri
    )
    if root_schema.get("$schema") != expected_dialect:
        raise SchemaGraphError(
            f"schema dialect mismatch for {root_uri}: expected {expected_dialect!r}"
        )
    try:
        Draft202012Validator.check_schema(root_schema)
        validator = Draft202012Validator(
            root_schema,
            registry=cast(Any, registry.referencing_registry()),
            format_checker=_format_checker(),
        )
        return _draft_issues(
            errors=validator.iter_errors(cast(Any, instance)),
            path=path,
        )
    except SchemaError as exc:
        raise SchemaGraphError(f"invalid Draft 2020-12 schema: {exc.message}") from exc
    except Unresolvable as exc:
        raise SchemaGraphError(f"unresolved local schema dependency: {exc}") from exc


def validate_draft_2020_12(
    instance: object,
    schema: dict[str, object],
    *,
    path: str,
) -> list[SchemaIssue]:
    """Validate one self-contained Draft 2020-12 schema with formats asserted."""

    try:
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema, format_checker=_format_checker())
        return _draft_issues(
            errors=validator.iter_errors(cast(Any, instance)),
            path=path,
        )
    except SchemaError as exc:
        raise SchemaGraphError(f"invalid Draft 2020-12 schema: {exc.message}") from exc
    except Unresolvable as exc:
        raise SchemaGraphError(f"unresolved local schema dependency: {exc}") from exc
