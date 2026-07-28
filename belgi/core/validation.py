from __future__ import annotations

from .evaluator.exceptions import SemanticConstructionError

__all__ = ["require_identifier"]


def require_identifier(*, owner: str, name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SemanticConstructionError(f"{owner} {name} must be a non-empty string.")
