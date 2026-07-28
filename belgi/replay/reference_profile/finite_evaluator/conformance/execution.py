"""Production-semantic observation of one finite evaluator input."""

from __future__ import annotations

from collections.abc import Mapping

import belgi.profile.reference_profile.finite_evaluator as finite_evaluator
from belgi.carrier import CarrierError, EvaluatorCarrier
from belgi.carrier.integrity import canonical_json_document_bytes
from belgi.core import (
    AdmissionSubject,
    JudgedObject,
    ReferenceContext,
    SatRegistry,
    apply_evaluator,
)
from belgi.profile.reference_profile.evaluator import (
    build_reference_profile_evaluator_sat_registry,
)
from belgi.profile.reference_profile.evidence import (
    reference_profile_evidence_kind_ownership_registry,
    reference_profile_evidence_state_from_carrier_items,
)
from belgi.profile.reference_profile.judged import (
    reference_profile_judged_object_from_carrier_endpoints,
)
from belgi.replay.carriers import parse_evaluator_carrier
from belgi.replay.lifting.exceptions import ReplayError
from belgi.replay.parsing import parse_declaration_parameters
from belgi.replay.reference_profile.evaluator.lifting import (
    reference_profile_evaluator_from_resolved_selection,
)
from belgi.replay.reference_profile.evidence.model import (
    ReferenceProfileEvidenceCarrierItem,
)
from belgi.replay.reference_profile.judged.model import (
    ReferenceProfileJudgedCarrierEndpoint,
)

_PART4_KEY = (
    finite_evaluator.PART4_DESIGNATOR.uri,
    finite_evaluator.PART4_DESIGNATOR.digest.algorithm_id,
    finite_evaluator.PART4_DESIGNATOR.digest.digest_value,
)


def observe_finite_evaluator_input(
    *, input_document: Mapping[str, object]
) -> dict[str, object]:
    """Derive one result without consulting corpus expectation fields."""

    prior_replay = _finite_execution_mapping(
        input_document.get("priorReplay"), label="priorReplay"
    )
    if prior_replay.get("status") != "succeeded":
        return _earlier_failure(prior_replay=prior_replay)
    _require_exact_part4_source(input_document.get("exactPart4Designator"))
    sat_registry = build_reference_profile_evaluator_sat_registry()

    judged, judged_error = _lift_judged(input_document=input_document)
    evidence, evidence_error = _lift_evidence(input_document=input_document)
    evaluator, evaluator_error = _lift_evaluator(
        input_document=input_document,
        sat_registry=sat_registry,
    )
    if judged_error is not None:
        return _lift_failure(stage="lambda_J")
    if evidence_error is not None:
        return _lift_failure(stage="lambda_E")
    if evaluator_error is not None:
        return _lift_failure(stage="lambda_F")
    if judged is None or evidence is None or evaluator is None:
        raise RuntimeError("finite evaluator lift result is internally incomplete.")

    verdict = int(
        apply_evaluator(
            evaluator=evaluator,
            judged=judged,
            evidence=evidence,
            sat_registry=sat_registry,
        )
    )
    warnings: list[str] = []
    if "cachedVerdict" in input_document:
        cached = input_document.get("cachedVerdict")
        if (
            not isinstance(cached, int)
            or isinstance(cached, bool)
            or cached not in {0, 1}
        ):
            raise ValueError("finite evaluator cachedVerdict must be 0 or 1.")
        if cached != verdict:
            warnings.append("cached-verdict-mismatch")
    return {
        "resultKind": "success",
        "verdict": verdict,
        "failureStage": None,
        "warnings": warnings,
        "finiteEvaluationPerformed": True,
    }


def _lift_judged(
    *, input_document: Mapping[str, object]
) -> tuple[JudgedObject | None, Exception | None]:
    try:
        if "preInducedOutsideFiniteSubsetPart1JudgedObject" in input_document:
            value = _finite_execution_mapping(
                input_document.get("preInducedOutsideFiniteSubsetPart1JudgedObject"),
                label="preInducedOutsideFiniteSubsetPart1JudgedObject",
            )
            if set(value) != {"admissionSubject", "referenceContext"}:
                raise ValueError("pre-induced judged object must be closed.")
            admission = _finite_execution_text(
                value.get("admissionSubject"), label="admissionSubject"
            )
            reference = _finite_execution_text(
                value.get("referenceContext"), label="referenceContext"
            )
            return (
                JudgedObject(
                    admission_subject=AdmissionSubject(value=admission),
                    reference_context=ReferenceContext(value=reference),
                ),
                None,
            )
        return (
            reference_profile_judged_object_from_carrier_endpoints(
                **_judged_carrier_endpoints(
                    document=_finite_execution_mapping(
                        input_document.get("judgedCarrier"),
                        label="judgedCarrier",
                    )
                ),
                resolved_determining_source_designators=(
                    finite_evaluator.PART4_DESIGNATOR,
                ),
            ),
            None,
        )
    except (CarrierError, ReplayError, ValueError) as exc:
        return None, exc


def _lift_evidence(*, input_document: Mapping[str, object]):
    try:
        carrier_items = _evidence_carrier_items(
            document=_finite_execution_mapping(
                input_document.get("evidenceCarrier"),
                label="evidenceCarrier",
            )
        )
        registry = reference_profile_evidence_kind_ownership_registry()
        return (
            reference_profile_evidence_state_from_carrier_items(
                carrier_items=carrier_items,
                resolved_owner_designators=(finite_evaluator.PART4_DESIGNATOR,),
                ownership_registry=registry,
            ),
            None,
        )
    except (CarrierError, ReplayError, ValueError) as exc:
        return None, exc


def _lift_evaluator(*, input_document: Mapping[str, object], sat_registry: SatRegistry):
    try:
        return (
            reference_profile_evaluator_from_resolved_selection(
                evaluator_carrier=_finite_execution_evaluator_carrier(
                    document=_finite_execution_mapping(
                        input_document.get("evaluatorCarrier"),
                        label="evaluatorCarrier",
                    )
                ),
                resolved_source_designators=frozenset({_PART4_KEY}),
                provider_witness_keys=_finite_execution_provider_witness_keys(
                    sat_registry=sat_registry
                ),
                finite_selection_authorized=True,
            ),
            None,
        )
    except (CarrierError, ReplayError, ValueError) as exc:
        return None, exc


def _finite_execution_provider_witness_keys(
    *, sat_registry: SatRegistry
) -> frozenset[tuple[tuple[str, str, str], str]]:
    keys: set[tuple[tuple[str, str, str], str]] = set()
    for witness in sat_registry.provider_witnesses():
        source_designator = getattr(witness, "source_designator", None)
        digest = getattr(source_designator, "digest", None)
        uri = getattr(source_designator, "uri", None)
        algorithm_id = getattr(digest, "algorithm_id", None)
        digest_value = getattr(digest, "digest_value", None)
        semantics_key = getattr(witness, "semantics_key", None)
        if not (
            isinstance(uri, str)
            and uri
            and isinstance(algorithm_id, str)
            and algorithm_id
            and isinstance(digest_value, str)
            and digest_value
        ):
            raise ValueError("production provider witness designator is incomplete.")
        if not isinstance(semantics_key, str) or not semantics_key:
            raise ValueError("production provider witness semantics key is invalid.")
        source_key = (uri, algorithm_id, digest_value)
        keys.add((source_key, semantics_key))
    return frozenset(keys)


def _judged_carrier_endpoints(
    *, document: Mapping[str, object]
) -> dict[str, ReferenceProfileJudgedCarrierEndpoint]:
    if set(document) != {"kind", "proposal", "baseline"}:
        raise ValueError("finite judged carrier must be closed.")
    if document.get("kind") != "judged-object-carrier":
        raise ValueError("finite judged carrier kind is unsupported.")
    return {
        "proposal": ReferenceProfileJudgedCarrierEndpoint(
            content=_inline_json_content(
                value=document.get("proposal"),
                label="judgedCarrier.proposal",
            )
        ),
        "baseline": ReferenceProfileJudgedCarrierEndpoint(
            content=_inline_json_content(
                value=document.get("baseline"),
                label="judgedCarrier.baseline",
            )
        ),
    }


def _evidence_carrier_items(
    *, document: Mapping[str, object]
) -> tuple[ReferenceProfileEvidenceCarrierItem, ...]:
    if set(document) != {"kind", "evidenceItems"}:
        raise ValueError("finite evidence carrier must be closed.")
    if document.get("kind") != "evidence-state-carrier":
        raise ValueError("finite evidence carrier kind is unsupported.")
    items = _finite_execution_mapping(
        document.get("evidenceItems"), label="evidenceItems"
    )
    adapted: list[ReferenceProfileEvidenceCarrierItem] = []
    for identifier, raw_item in sorted(items.items()):
        if not isinstance(identifier, str) or not identifier:
            raise ValueError("finite evidence identifier must be non-empty text.")
        item = _finite_execution_mapping(raw_item, label=f"evidenceItems.{identifier}")
        item_fields = set(item)
        if item_fields not in (
            {"evidenceKindIdentifier", "source", "parameters"},
            {"evidenceKindIdentifier", "source"},
        ):
            raise ValueError(f"finite evidence item {identifier!r} must be closed.")
        kind = _finite_execution_text(
            item.get("evidenceKindIdentifier"),
            label=f"evidenceItems.{identifier}.evidenceKindIdentifier",
        )
        adapted.append(
            ReferenceProfileEvidenceCarrierItem(
                evidence_identifier=identifier,
                evidence_kind_identifier=kind,
                source_json_content=_finite_execution_mapping(
                    _inline_json_content(
                        value=item.get("source"),
                        label=f"evidenceItems.{identifier}.source",
                    ),
                    label=f"evidenceItems.{identifier}.source.content",
                ),
                source_media_type="application/json",
                source_preserved_octets=None,
                parameters=parse_declaration_parameters(
                    payload=item.get("parameters"),
                    description=f"evidenceItems.{identifier}.parameters",
                ),
            )
        )
    return tuple(adapted)


def _finite_execution_evaluator_carrier(
    *, document: Mapping[str, object]
) -> EvaluatorCarrier:
    return parse_evaluator_carrier(
        root_bytes=canonical_json_document_bytes(document=document),
        description="finite evaluator carrier",
    )


def _inline_json_content(*, value: object, label: str) -> object:
    locator = _finite_execution_mapping(value, label=label)
    if set(locator) != {"kind", "mediaType", "content"}:
        raise ValueError(f"finite {label} locator must be closed.")
    if (
        locator.get("kind") != "inline-json"
        or locator.get("mediaType") != "application/json"
    ):
        raise ValueError(f"finite {label} must be resolved inline JSON.")
    return locator.get("content")


def _require_exact_part4_source(value: object) -> None:
    designator = _finite_execution_mapping(value, label="exactPart4Designator")
    digest = _finite_execution_mapping(
        designator.get("digest"), label="exactPart4Designator.digest"
    )
    observed = (
        designator.get("uri"),
        digest.get("algorithmId"),
        digest.get("digestValue"),
    )
    if observed != _PART4_KEY:
        raise ValueError("finite evaluator input did not resolve exact Part 4.")


def _earlier_failure(*, prior_replay: Mapping[str, object]) -> dict[str, object]:
    stage = _finite_execution_text(
        prior_replay.get("failureStage"), label="prior failureStage"
    )
    return {
        "resultKind": "earlier-failure",
        "verdict": None,
        "failureStage": stage,
        "warnings": [],
        "finiteEvaluationPerformed": False,
    }


def _lift_failure(*, stage: str) -> dict[str, object]:
    return {
        "resultKind": "lift-failure",
        "verdict": None,
        "failureStage": stage,
        "warnings": [],
        "finiteEvaluationPerformed": True,
    }


def _finite_execution_mapping(value: object, *, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"finite evaluator {label} must be an object.")
    return value


def _finite_execution_text(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"finite evaluator {label} must be non-empty text.")
    return value
