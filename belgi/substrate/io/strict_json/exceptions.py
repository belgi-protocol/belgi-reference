from __future__ import annotations

from .model import JSONValidationStage


class JSONDomainError(ValueError):
    """Structured failure from the strict JSON representation boundary."""

    def __init__(
        self,
        *,
        stage: JSONValidationStage,
        code: str,
        detail: str,
    ) -> None:
        super().__init__(detail)
        self.stage: JSONValidationStage = stage
        self.code: str = code


__all__ = ["JSONDomainError"]
