"""Package-representation rejection exceptions."""

from __future__ import annotations

from .model import RepresentationResult

__all__ = ["DirectoryEntrySetError", "PackageRepresentationError"]


class PackageRepresentationError(ValueError):
    def __init__(self, result: RepresentationResult) -> None:
        if result.accepted:
            raise ValueError("accepted result cannot be raised as an error")
        result_description = result.result_code.replace("-", " ")
        super().__init__(
            f"package representation rejected at stage {result.stage}: "
            f"{result_description} ({result.result_code})"
        )
        self.result = result


class DirectoryEntrySetError(Exception):
    def __init__(self, result_code: str) -> None:
        super().__init__(result_code)
        self.result_code = result_code
