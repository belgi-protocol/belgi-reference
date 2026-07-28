from __future__ import annotations

from typing import Any

from belgi.substrate.schema.exceptions import SchemaGraphError
from belgi.substrate.schema.model import SchemaIssue
from belgi.substrate.schema.walker import validate_draft_2020_12


def require_schema_object(obj: Any, *, label: str) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise ValueError(f"{label} must be a JSON object")
    return obj


def format_first_schema_issue(issues: list[SchemaIssue], *, label: str) -> str:
    if not issues:
        raise ValueError("schema_issues missing/empty")
    first = issues[0]
    return f"{label} invalid at {first.path}: {first.message}"


def validate_schema(
    obj: Any, schema: dict[str, Any], *, root_schema: dict[str, Any], path: str
) -> list[SchemaIssue]:
    """Validate through the repository's Draft 2020-12 mechanism owner."""

    if "$ref" in schema and not isinstance(schema.get("$ref"), str):
        return [SchemaIssue(path=path, message="$ref must be string")]
    validation_schema: dict[str, object]
    if schema is root_schema:
        validation_schema = root_schema
    else:
        root_definitions = root_schema.get("$defs", {})
        if not isinstance(root_definitions, dict):
            return [SchemaIssue(path=path, message="$defs must be an object")]
        target_name = "__belgi_validation_target__"
        if target_name in root_definitions:
            return [SchemaIssue(path=path, message="reserved validation target exists")]
        validation_schema = {
            "$schema": root_schema.get(
                "$schema",
                "https://json-schema.org/draft/2020-12/schema",
            ),
            "$defs": {**root_definitions, target_name: schema},
            "$ref": f"#/$defs/{target_name}",
        }
    try:
        return validate_draft_2020_12(obj, validation_schema, path=path)
    except SchemaGraphError as exc:
        return [SchemaIssue(path=path, message=f"unresolvable $ref: {exc}")]
