"""Reference-profile exception hierarchy."""

from __future__ import annotations

from belgi.profile.exceptions import ProfileError

__all__ = [
    "ReferenceProfileAdmissionCompileError",
    "ReferenceProfileEvaluatorCompileError",
    "ReferenceProfileEvidenceStateCompileError",
    "ReferenceProfileJudgedObjectCompileError",
    "ReferenceProfileReplayError",
    "ReferenceProfileSourceStateError",
]


class ReferenceProfileAdmissionCompileError(ProfileError, ValueError):
    """Raised when profile-owned admission compilation cannot recover one semantic slice."""

    def __init__(self, *, semantic_slice: str, detail: str) -> None:
        self.semantic_slice = semantic_slice
        super().__init__(
            f"reference-profile admission compile failure [{semantic_slice}]: {detail}"
        )


class ReferenceProfileEvaluatorCompileError(ProfileError, ValueError):
    """Raised when profile-owned evaluator compilation cannot recover one semantic slice."""

    def __init__(self, *, semantic_slice: str, detail: str) -> None:
        self.semantic_slice = semantic_slice
        super().__init__(
            f"reference-profile evaluator compile failure [{semantic_slice}]: {detail}"
        )


class ReferenceProfileJudgedObjectCompileError(ProfileError, ValueError):
    """Raised when profile-owned judged-object compilation cannot recover one semantic slice."""

    def __init__(self, *, semantic_slice: str, detail: str) -> None:
        self.semantic_slice = semantic_slice
        super().__init__(
            "reference-profile judged-object compile failure "
            f"[{semantic_slice}]: {detail}"
        )


class ReferenceProfileEvidenceStateCompileError(ProfileError, ValueError):
    """Raised when profile-owned evidence-state compilation cannot recover one semantic slice."""

    def __init__(self, *, semantic_slice: str, detail: str) -> None:
        self.semantic_slice = semantic_slice
        super().__init__(
            "reference-profile evidence-state compile failure "
            f"[{semantic_slice}]: {detail}"
        )


class ReferenceProfileReplayError(ValueError):
    """Raised when the reference-profile replay procedure cannot recover a tuple."""


class ReferenceProfileSourceStateError(ProfileError, ValueError):
    """Raised when profile-owned judged source-state meaning is invalid."""

    def __init__(self, *, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)
