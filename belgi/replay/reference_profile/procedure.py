from __future__ import annotations

from typing import TypeAlias

from belgi.carrier import (
    EvaluatorCarrier,
    EvidenceStateCarrier,
    JudgedObjectCarrier,
)
from belgi.core import Evaluator, EvidenceState, JudgedObject, SatRegistry, Verdict
from belgi.profile.reference_profile import ReferenceProfileReplayError
from belgi.profile.reference_profile.environment import (
    evidence_uses_environment_envelope,
    require_environment_compatibility_condition,
)
from belgi.profile.reference_profile.evaluator import (
    build_reference_profile_evaluator_sat_registry,
)
from belgi.profile.reference_profile.evidence import (
    EvidenceKindOwnershipRegistry,
    reference_profile_evidence_kind_ownership_registry,
)
from belgi.replay.context import PackageIntegrityAnchorVerifier, ReplayContext
from belgi.replay.package_integrity_anchor.bootstrap import (
    installed_package_integrity_anchor_verifier,
)
from belgi.replay.package_source.protocol import ReplayPackageSource
from belgi.replay.procedure.execution import run_replay_procedure
from belgi.replay.procedure.model import ReplayExecution
from belgi.replay.verdict import core_verdict_deriver

from .evaluator import EvaluatorReferenceProfileAdapter
from .evidence import EvidenceStateReferenceProfileAdapter
from .evidence.resolution import ResolvedReferenceProfileEvidenceStateCarrier
from .judged import JudgedObjectReferenceProfileAdapter
from .judged.part4_source_state import Part4JudgedSourceStateExtension

__all__ = [
    "ReferenceProfileReplayContext",
    "ReferenceProfileReplayExecution",
    "build_reference_profile_replay_context",
    "derive_reference_profile_verdict",
    "recover_reference_profile_execution",
    "reference_profile_replay_context",
]


ReferenceProfileReplayContext: TypeAlias = ReplayContext[
    JudgedObjectCarrier,
    JudgedObjectCarrier,
    EvidenceStateCarrier,
    ResolvedReferenceProfileEvidenceStateCarrier,
    EvaluatorCarrier,
    EvaluatorCarrier,
    JudgedObject,
    EvidenceState,
    Evaluator,
    Verdict,
]
ReferenceProfileReplayExecution: TypeAlias = ReplayExecution[
    JudgedObjectCarrier,
    JudgedObjectCarrier,
    EvidenceStateCarrier,
    ResolvedReferenceProfileEvidenceStateCarrier,
    EvaluatorCarrier,
    EvaluatorCarrier,
    JudgedObject,
    EvidenceState,
    Evaluator,
    Verdict,
]


def _reference_profile_verdict_deriver(*, sat_registry: SatRegistry):
    derive_verdict = core_verdict_deriver(sat_registry=sat_registry)

    def derive(
        *,
        judged: JudgedObject,
        evidence: EvidenceState,
        evaluator: Evaluator,
    ) -> Verdict:
        require_environment_compatibility_condition(
            declared_condition_ids=evaluator.declared_condition_ids,
            environment_envelope_present=(
                evidence_uses_environment_envelope(evidence=evidence)
            ),
            surface_label="environment-envelope material",
        )
        return derive_verdict(judged=judged, evidence=evidence, evaluator=evaluator)

    return derive


def build_reference_profile_replay_context(
    *,
    package_integrity_anchor_verifier: PackageIntegrityAnchorVerifier,
    sat_registry: SatRegistry,
    evidence_kind_ownership_registry: (EvidenceKindOwnershipRegistry | None) = None,
    judged_lifting: JudgedObjectReferenceProfileAdapter | None = None,
) -> ReferenceProfileReplayContext:
    active_evidence_kind_owners = (
        reference_profile_evidence_kind_ownership_registry()
        if evidence_kind_ownership_registry is None
        else evidence_kind_ownership_registry
    )
    return ReplayContext(
        judged_lifting=(
            JudgedObjectReferenceProfileAdapter(
                source_state_extension=Part4JudgedSourceStateExtension(),
            )
            if judged_lifting is None
            else judged_lifting
        ),
        evidence_lifting=EvidenceStateReferenceProfileAdapter(
            ownership_registry=active_evidence_kind_owners
        ),
        evaluator_lifting=EvaluatorReferenceProfileAdapter(
            provider_witnesses=sat_registry.provider_witnesses(),
        ),
        package_integrity_anchor_verifier=package_integrity_anchor_verifier,
        verdict_deriver=_reference_profile_verdict_deriver(
            sat_registry=sat_registry,
        ),
    )


def reference_profile_replay_context(
    *,
    judged_lifting: JudgedObjectReferenceProfileAdapter | None = None,
) -> ReferenceProfileReplayContext:
    return build_reference_profile_replay_context(
        package_integrity_anchor_verifier=installed_package_integrity_anchor_verifier(),
        sat_registry=build_reference_profile_evaluator_sat_registry(),
        judged_lifting=judged_lifting,
    )


def recover_reference_profile_execution(
    *,
    package_source: ReplayPackageSource,
    judged_lifting: JudgedObjectReferenceProfileAdapter | None = None,
) -> ReferenceProfileReplayExecution:
    return run_replay_procedure(
        package=package_source,
        replay_context=reference_profile_replay_context(
            judged_lifting=judged_lifting,
        ),
    )


def _require_successful_execution(
    *,
    package_source: ReplayPackageSource,
) -> ReferenceProfileReplayExecution:
    execution = recover_reference_profile_execution(package_source=package_source)
    if not execution.successful:
        raise ReferenceProfileReplayError(
            f"Reference-profile replay failed: {execution.report.problems!r}"
        )
    semantic_tuple = execution.semantic_tuple
    derived_verdict = execution.derived_verdict
    if semantic_tuple is None or derived_verdict is None:
        raise ReferenceProfileReplayError(
            "Reference-profile replay did not recover both semantic tuple and verdict."
        )
    if execution.evaluator_trace is None:
        raise ReferenceProfileReplayError(
            "Reference-profile replay did not retain evaluator lifting trace."
        )
    return execution


def derive_reference_profile_verdict(
    *,
    package_source: ReplayPackageSource,
) -> int:
    execution = _require_successful_execution(package_source=package_source)
    derived_verdict = execution.derived_verdict
    if derived_verdict is None:
        raise ReferenceProfileReplayError(
            "Reference-profile replay did not recover a verdict."
        )
    return int(derived_verdict)
