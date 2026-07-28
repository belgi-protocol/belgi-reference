from __future__ import annotations

__all__ = [
    "CoreError",
    "DuplicateIdentifierError",
    "DuplicateSatRegistrationError",
    "EvaluatorError",
    "EvaluatorModelError",
    "ProjectionError",
    "SatExecutionError",
    "SatRegistryError",
    "SemanticConstructionError",
]


class CoreError(Exception):
    pass


class SemanticConstructionError(CoreError):
    pass


class ProjectionError(SemanticConstructionError):
    pass


class EvaluatorError(CoreError):
    pass


class EvaluatorModelError(EvaluatorError):
    pass


class DuplicateIdentifierError(EvaluatorModelError):
    pass


class SatRegistryError(EvaluatorError):
    pass


class DuplicateSatRegistrationError(SatRegistryError):
    pass


class SatExecutionError(EvaluatorError):
    pass
