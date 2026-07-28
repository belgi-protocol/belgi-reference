"""Lift failures owned by the Part 4 finite evaluator."""


class FiniteJudgedLiftError(ValueError):
    """The finite judged-object lift is undefined."""


class FiniteEvidenceLiftError(ValueError):
    """The finite evidence-state lift is undefined."""


class FiniteEvaluatorLiftError(ValueError):
    """The finite evaluator lift is undefined."""
