from __future__ import annotations

from belgi.profile.governance import EvaluatorParameterId

__all__ = [
    "ALL_PARAMETER_IDS",
    "ANALYSIS_SCOPE_PARAMETER",
    "COVERAGE_MINIMUM_PARAMETER",
    "DEPENDENCY_SET_DESIGNATOR_PARAMETER",
    "ENVIRONMENT_CONSTRAINT_PARAMETER",
    "FAILURE_THRESHOLD_PARAMETER",
    "INTERPRETER_CONSTRAINT_PARAMETER",
]


ANALYSIS_SCOPE_PARAMETER = EvaluatorParameterId("belgi.python.parameter.analysis-scope")
COVERAGE_MINIMUM_PARAMETER = EvaluatorParameterId(
    "belgi.python.parameter.coverage-minimum"
)
DEPENDENCY_SET_DESIGNATOR_PARAMETER = EvaluatorParameterId(
    "belgi.python.parameter.dependency-set-designator"
)
ENVIRONMENT_CONSTRAINT_PARAMETER = EvaluatorParameterId(
    "belgi.python.parameter.environment-constraint"
)
FAILURE_THRESHOLD_PARAMETER = EvaluatorParameterId(
    "belgi.python.parameter.failure-threshold"
)
INTERPRETER_CONSTRAINT_PARAMETER = EvaluatorParameterId(
    "belgi.python.parameter.interpreter-constraint"
)

ALL_PARAMETER_IDS: tuple[EvaluatorParameterId, ...] = (
    ANALYSIS_SCOPE_PARAMETER,
    FAILURE_THRESHOLD_PARAMETER,
    COVERAGE_MINIMUM_PARAMETER,
    DEPENDENCY_SET_DESIGNATOR_PARAMETER,
    INTERPRETER_CONSTRAINT_PARAMETER,
    ENVIRONMENT_CONSTRAINT_PARAMETER,
)
