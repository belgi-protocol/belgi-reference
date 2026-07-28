"""Integrated observation of physical representation and replay truth."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from belgi.replay.instructions import REPLAY_STEP_ORDER
from belgi.replay.package_representation.exceptions import PackageRepresentationError
from belgi.replay.package_representation.model import RepresentationResult
from belgi.replay.package_source.physical_attempt import (
    PhysicalReplayPackageSourceAttempt,
)
from belgi.replay.procedure.model import ReplayExecution
from belgi.replay.report import failed_report
from belgi.replay.verification.claim_record.read import read_claim_record

_AnyReplayExecution = ReplayExecution[Any, Any, Any, Any, Any, Any, Any, Any, Any, Any]


@dataclass(frozen=True, slots=True, kw_only=True)
class PhysicalReplayObservation:
    representation_result: RepresentationResult | None
    execution: _AnyReplayExecution | None

    def __post_init__(self) -> None:
        result = self.representation_result
        execution = self.execution
        if result is None:
            if (
                execution is None
                or execution.successful
                or not execution.report.problems
            ):
                raise ValueError(
                    "Representation-pending observation requires a Part-2 failure."
                )
            step = execution.report.problems[0].governing_step
            if str(step) not in {
                "step-2-verify-claim-record-integrity-binding-presence",
                "step-3-verify-claim-record-integrity",
                "step-4-validate-authenticated-claim-record",
            }:
                raise ValueError(
                    "Representation-pending failure must terminate at Part-2 Step 2-4."
                )
            return
        if result.accepted:
            if result.stage != 8 or result.result_code != "complete":
                raise ValueError("Accepted representation must be Stage-8 complete.")
            if execution is None:
                raise ValueError("Stage-8 complete requires a Part-2 execution.")
            if execution.report.problems:
                first_step = execution.report.problems[0].governing_step
                if REPLAY_STEP_ORDER.index(first_step) < 4:
                    raise ValueError(
                        "Stage-8 complete cannot precede a Step 1-4 failure."
                    )
            return
        if result.stage == 6:
            if (
                execution is None
                or execution.successful
                or not execution.report.problems
                or str(execution.report.problems[0].type) != "malformed-claim-record"
                or str(execution.report.problems[0].governing_step)
                != "step-1-read-claim-record"
            ):
                raise ValueError(
                    "Stage-6 rejection requires its Part-2 Step-1 malformed problem."
                )
            return
        if execution is not None or result.stage not in {1, 2, 3, 4, 5, 7}:
            raise ValueError(
                "Stage 1-5/7 representation rejection must remain representation-only."
            )


def observe_physical_replay(
    *,
    attempt: PhysicalReplayPackageSourceAttempt,
    recover: Callable[..., _AnyReplayExecution],
) -> PhysicalReplayObservation:
    """Retain typed representation truth and any applicable Part-2 result."""

    if attempt.source is not None:
        try:
            execution = recover(package_source=attempt.source)
        except PackageRepresentationError as exc:
            return PhysicalReplayObservation(
                representation_result=exc.result,
                execution=None,
            )
        return PhysicalReplayObservation(
            representation_result=execution.representation_result,
            execution=execution,
        )
    snapshot = attempt.step1_snapshot()
    if snapshot is None:
        return PhysicalReplayObservation(
            representation_result=attempt.representation_rejection,
            execution=None,
        )
    _, _, problems, package_identifier = read_claim_record(package=snapshot)
    if not problems:
        raise RuntimeError(
            "Rejected Stage-6 snapshot did not produce its required Step-1 problem."
        )
    return PhysicalReplayObservation(
        representation_result=attempt.representation_rejection,
        execution=ReplayExecution(
            report=failed_report(
                package_identifier=package_identifier,
                problems=problems,
            )
        ),
    )


__all__ = ["PhysicalReplayObservation", "observe_physical_replay"]
