from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from belgi.carrier import ClaimRecord, PackageIdentifier
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
from belgi.replay.instructions import (
    STANDARD_REPLAY_INSTRUCTIONS,
    STEP_DERIVE_VERDICT,
    STEP_LIFT_SEMANTIC_OBJECTS,
    ReplayInstructions,
)
from belgi.replay.lifting.model import LiftingTrace
from belgi.replay.package_representation.model import RepresentationResult
from belgi.replay.package_source.protocol import ReplayPackageSource
from belgi.replay.problems import (
    INDUCE_FAILURE,
    NON_DETERMINISTIC_LIFT,
    ReplayProblem,
    build_replay_problem,
)
from belgi.replay.procedure.determinism import (
    framework_recovery_values_match,
    semantic_results_match,
)
from belgi.replay.procedure.lifting import recover_semantic_traces
from belgi.replay.procedure.model import (
    RecoveredLiftingTraces,
    RecoveredSemanticTuple,
    ReplayExecution,
)
from belgi.replay.procedure.outcome import (
    binding_matches_from_traces,
    cached_verdict_warning,
)
from belgi.replay.procedure.verification import verify_replay_package
from belgi.replay.report import ReplayWarning, failed_report, successful_report
from belgi.replay.verification.claim_record.required_roots import ValidatedRoots

__all__ = ["run_replay_procedure"]


@dataclass(frozen=True, slots=True, kw_only=True)
class _RecoveredReplayResult:
    traces: RecoveredLiftingTraces[Any, Any, Any, Any, Any, Any, Any, Any, Any] | None
    semantic_tuple: RecoveredSemanticTuple[Any, Any, Any] | None
    derived_verdict: Any | None
    problem: ReplayProblem | None


def run_replay_procedure(
    *,
    package: ReplayPackageSource,
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
    instructions: ReplayInstructions = STANDARD_REPLAY_INSTRUCTIONS,
) -> ReplayExecution[
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
]:
    verification = verify_replay_package(
        package=package,
        package_integrity_anchor_verifier=(
            replay_context.package_integrity_anchor_verifier
        ),
    )
    if verification.problems:
        return _failure_execution(
            package_identifier=verification.package_identifier,
            claim_record=verification.claim_record,
            representation_result=verification.representation_result,
            problems=verification.problems,
        )
    claim_record = verification.claim_record
    roots = verification.roots
    package_identifier = verification.package_identifier
    if claim_record is None or roots is None or package_identifier is None:
        raise RuntimeError(
            "Replay package verification succeeded without a claim record, roots, "
            "and package identifier."
        )

    results = tuple(
        _recover_replay_result(
            package=package,
            claim_record=claim_record,
            roots=roots,
            replay_context=replay_context,
        )
        for _ in range(instructions.repeatability_checks)
    )
    first = results[0]
    for repeated in results[1:]:
        if first.problem is not None or repeated.problem is not None:
            if (
                first.problem is not None
                and repeated.problem is not None
                and framework_recovery_values_match(
                    left=first.problem,
                    right=repeated.problem,
                )
            ):
                continue
            return _non_deterministic_execution(
                package_identifier=package_identifier,
                claim_record=claim_record,
                first=first,
                representation_result=verification.representation_result,
                detail="Repeated semantic recovery did not reproduce the same failure.",
            )
        if (
            first.traces is None
            or repeated.traces is None
            or first.semantic_tuple is None
            or repeated.semantic_tuple is None
            or first.derived_verdict is None
            or repeated.derived_verdict is None
        ):
            raise RuntimeError(
                "Successful semantic recovery returned incomplete state."
            )
        if not semantic_results_match(
            first_traces=first.traces,
            repeated_traces=repeated.traces,
            first_tuple=first.semantic_tuple,
            repeated_tuple=repeated.semantic_tuple,
        ) or not framework_recovery_values_match(
            left=first.derived_verdict,
            right=repeated.derived_verdict,
        ):
            return _non_deterministic_execution(
                package_identifier=package_identifier,
                claim_record=claim_record,
                first=first,
                representation_result=verification.representation_result,
                detail=(
                    "Repeated semantic recovery produced a different semantic tuple "
                    "or derived verdict."
                ),
            )
    if first.problem is not None:
        traces = first.traces
        return _failure_execution(
            package_identifier=package_identifier,
            claim_record=claim_record,
            representation_result=verification.representation_result,
            problems=(first.problem,),
            judged_trace=None if traces is None else traces.judged,
            evidence_trace=None if traces is None else traces.evidence,
            evaluator_trace=None if traces is None else traces.evaluator,
        )
    traces = first.traces
    semantic_tuple = first.semantic_tuple
    derived_verdict = first.derived_verdict
    if traces is None or semantic_tuple is None or derived_verdict is None:
        raise RuntimeError("Successful semantic recovery returned incomplete state.")

    warning = cached_verdict_warning(
        claim_record=claim_record,
        derived_verdict=derived_verdict,
    )
    warnings: tuple[ReplayWarning, ...] = () if warning is None else (warning,)
    return ReplayExecution(
        report=successful_report(
            package_identifier=package_identifier,
            derived_verdict=derived_verdict,
            warnings=warnings,
        ),
        claim_record=claim_record,
        representation_result=verification.representation_result,
        semantic_tuple=semantic_tuple,
        judged_trace=traces.judged,
        evidence_trace=traces.evidence,
        evaluator_trace=traces.evaluator,
        binding_matches=binding_matches_from_traces(
            evidence_trace=traces.evidence,
            evaluator_trace=traces.evaluator,
        ),
    )


def _recover_replay_result(
    *,
    package: ReplayPackageSource,
    claim_record: ClaimRecord,
    roots: ValidatedRoots,
    replay_context: ReplayContext[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any],
) -> _RecoveredReplayResult:
    traces, lifting_problem = recover_semantic_traces(
        package=package,
        claim_record=claim_record,
        roots=roots,
        replay_context=replay_context,
    )
    if lifting_problem is not None:
        return _RecoveredReplayResult(
            traces=None,
            semantic_tuple=None,
            derived_verdict=None,
            problem=lifting_problem,
        )
    if traces is None:
        raise RuntimeError("Semantic lifting succeeded without recovered traces.")
    try:
        derived_verdict = replay_context.verdict_deriver(
            judged=traces.judged.induced.value,
            evidence=traces.evidence.induced.value,
            evaluator=traces.evaluator.induced.value,
        )
    except Exception as exc:
        return _RecoveredReplayResult(
            traces=traces,
            semantic_tuple=None,
            derived_verdict=None,
            problem=build_replay_problem(
                problem_type=INDUCE_FAILURE,
                title="Verdict derivation failed.",
                detail=str(exc),
                governing_step=STEP_DERIVE_VERDICT,
            ),
        )
    return _RecoveredReplayResult(
        traces=traces,
        semantic_tuple=RecoveredSemanticTuple(
            judged=traces.judged.induced.value,
            evidence=traces.evidence.induced.value,
            evaluator=traces.evaluator.induced.value,
        ),
        derived_verdict=derived_verdict,
        problem=None,
    )


def _non_deterministic_execution(
    *,
    package_identifier: PackageIdentifier,
    claim_record: ClaimRecord,
    first: _RecoveredReplayResult,
    representation_result: RepresentationResult | None,
    detail: str,
) -> ReplayExecution[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]:
    traces = first.traces
    return _failure_execution(
        package_identifier=package_identifier,
        claim_record=claim_record,
        representation_result=representation_result,
        problems=(
            build_replay_problem(
                problem_type=NON_DETERMINISTIC_LIFT,
                title="Repeated semantic recovery was not deterministic.",
                detail=detail,
                governing_step=STEP_LIFT_SEMANTIC_OBJECTS,
            ),
        ),
        judged_trace=None if traces is None else traces.judged,
        evidence_trace=None if traces is None else traces.evidence,
        evaluator_trace=None if traces is None else traces.evaluator,
    )


def _failure_execution(
    *,
    package_identifier: PackageIdentifier | None,
    claim_record: ClaimRecord | None,
    representation_result: RepresentationResult | None = None,
    problems: tuple[ReplayProblem, ...],
    warnings: tuple[ReplayWarning, ...] = (),
    judged_trace: LiftingTrace[JudgedParsedT, JudgedResolvedT, JudgedT] | None = None,
    evidence_trace: LiftingTrace[EvidenceParsedT, EvidenceResolvedT, EvidenceT]
    | None = None,
    evaluator_trace: LiftingTrace[EvaluatorParsedT, EvaluatorResolvedT, EvaluatorT]
    | None = None,
) -> ReplayExecution[
    JudgedParsedT,
    JudgedResolvedT,
    EvidenceParsedT,
    EvidenceResolvedT,
    EvaluatorParsedT,
    EvaluatorResolvedT,
    JudgedT,
    EvidenceT,
    EvaluatorT,
    Any,
]:
    return ReplayExecution(
        report=failed_report(
            package_identifier=package_identifier,
            problems=problems,
            warnings=warnings,
        ),
        claim_record=claim_record,
        representation_result=representation_result,
        judged_trace=judged_trace,
        evidence_trace=evidence_trace,
        evaluator_trace=evaluator_trace,
    )
