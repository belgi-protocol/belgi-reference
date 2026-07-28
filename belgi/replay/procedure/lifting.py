from __future__ import annotations

from belgi.carrier import ClaimRecord
from belgi.replay.context import (
    EvaluatorParsedT,
    EvaluatorResolvedT,
    EvaluatorT,
    EvidenceParsedT,
    EvidenceResolvedT,
    EvidenceT,
    JudgedParsedT,
    JudgedResolvedT,
    JudgedT,
    ReplayContext,
    VerdictT,
)
from belgi.replay.instructions import STEP_LIFT_SEMANTIC_OBJECTS
from belgi.replay.lifting.exceptions import (
    AmbientContextRequiredError,
    InduceFailureError,
    LiftingStageError,
    ParseFailureError,
    ResolveFailureError,
)
from belgi.replay.lifting.lambda_e import lift_evidence_state
from belgi.replay.lifting.lambda_f import lift_evaluator
from belgi.replay.lifting.lambda_j import lift_judged_object
from belgi.replay.package_source.protocol import ReplayPackageSource
from belgi.replay.problems import (
    AMBIENT_CONTEXT_REQUIRED_PROBLEM,
    CARRIER_PARSE_FAILURE,
    CARRIER_RESOLVE_FAILURE,
    INDUCE_FAILURE,
    ReplayProblem,
    ReplayProblemType,
    build_replay_problem,
)
from belgi.replay.procedure.model import RecoveredLiftingTraces
from belgi.replay.verification.claim_record import ValidatedRoots

__all__ = ["recover_semantic_traces"]


def recover_semantic_traces(
    *,
    package: ReplayPackageSource,
    claim_record: ClaimRecord,
    roots: ValidatedRoots,
    replay_context: ReplayContext[
        JudgedParsedT,
        JudgedResolvedT,
        EvidenceParsedT,
        EvidenceResolvedT,
        EvaluatorParsedT,
        EvaluatorResolvedT,
        JudgedT,
        EvidenceT,
        EvaluatorT,
        VerdictT,
    ],
) -> tuple[
    RecoveredLiftingTraces[
        JudgedParsedT,
        JudgedResolvedT,
        EvidenceParsedT,
        EvidenceResolvedT,
        EvaluatorParsedT,
        EvaluatorResolvedT,
        JudgedT,
        EvidenceT,
        EvaluatorT,
    ]
    | None,
    ReplayProblem | None,
]:
    try:
        judged_trace = lift_judged_object(
            package=package,
            claim_record=claim_record,
            root_member=roots.judged,
            replay_context=replay_context,
        )
        evidence_trace = lift_evidence_state(
            package=package,
            claim_record=claim_record,
            root_member=roots.evidence,
            replay_context=replay_context,
        )
        evaluator_trace = lift_evaluator(
            package=package,
            claim_record=claim_record,
            root_member=roots.evaluator,
            replay_context=replay_context,
        )
    except ParseFailureError as exc:
        return None, _lifting_problem(
            error=exc,
            problem_type=CARRIER_PARSE_FAILURE,
            title="Carrier parsing failed.",
        )
    except AmbientContextRequiredError as exc:
        return None, _lifting_problem(
            error=exc,
            problem_type=AMBIENT_CONTEXT_REQUIRED_PROBLEM,
            title="Replay requires undeclared ambient context.",
        )
    except ResolveFailureError as exc:
        return None, _lifting_problem(
            error=exc,
            problem_type=CARRIER_RESOLVE_FAILURE,
            title="Carrier resolution failed.",
        )
    except InduceFailureError as exc:
        return None, _lifting_problem(
            error=exc,
            problem_type=INDUCE_FAILURE,
            title="Semantic induction failed.",
        )
    return (
        RecoveredLiftingTraces(
            judged=judged_trace,
            evidence=evidence_trace,
            evaluator=evaluator_trace,
        ),
        None,
    )


def _lifting_problem(
    *,
    error: LiftingStageError,
    problem_type: ReplayProblemType,
    title: str,
) -> ReplayProblem:
    return build_replay_problem(
        problem_type=problem_type,
        title=title,
        detail=str(error),
        governing_step=STEP_LIFT_SEMANTIC_OBJECTS,
        related_reference=error.related_reference,
    )
