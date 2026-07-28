from __future__ import annotations

from typing import Literal, TypeAlias

JSONValidationStage: TypeAlias = Literal["utf8", "json-syntax", "json-domain"]

__all__ = ["JSONValidationStage"]
