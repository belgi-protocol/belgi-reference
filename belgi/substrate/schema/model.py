from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeAlias


@dataclass(frozen=True, slots=True)
class SchemaIssue:
    path: str
    message: str
    keyword: str | None = None


IssueRecorder: TypeAlias = Callable[[str, str], None]
SchemaWalker: TypeAlias = Callable[[Any, Any, str], None]
