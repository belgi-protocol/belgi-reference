from __future__ import annotations


class SchemaGraphError(ValueError):
    """The selected local schema graph cannot be proven complete."""


__all__ = ["SchemaGraphError"]
