"""Claim-record required-root verification."""

from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier import (
    CanonicalReference,
    ClaimRecord,
    MemberInventoryEntry,
    MemberRole,
)
from belgi.carrier.inventory import MemberError
from belgi.replay.instructions import STEP_VERIFY_REQUIRED_ROOTS
from belgi.replay.problems import (
    DUPLICATE_ROOT_DESIGNATION,
    MISSING_REQUIRED_ROOT,
    ReplayProblem,
    build_replay_problem,
)

__all__ = ["ValidatedRoots", "validate_required_roots"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ValidatedRoots:
    judged: MemberInventoryEntry
    evidence: MemberInventoryEntry
    evaluator: MemberInventoryEntry


def validate_required_roots(
    *,
    claim_record: ClaimRecord,
) -> tuple[ValidatedRoots | None, tuple[ReplayProblem, ...]]:
    problems: list[ReplayProblem] = []
    root_references = (
        (
            claim_record.root_designators.judged_object_carrier_reference,
            "judged-object",
        ),
        (
            claim_record.root_designators.evidence_state_carrier_reference,
            "evidence-state",
        ),
        (
            claim_record.root_designators.evaluator_carrier_reference,
            "evaluator",
        ),
    )
    seen_references: set[CanonicalReference] = set()
    duplicate_references: set[CanonicalReference] = set()
    for reference, _label in root_references:
        if reference in seen_references:
            duplicate_references.add(reference)
        seen_references.add(reference)
    for reference in duplicate_references:
        problems.append(
            build_replay_problem(
                problem_type=DUPLICATE_ROOT_DESIGNATION,
                title="Required root designator is not unique.",
                detail=(
                    f"Canonical reference {reference!r} is designated for more "
                    "than one required carrier root."
                ),
                governing_step=STEP_VERIFY_REQUIRED_ROOTS,
                related_reference=reference,
            )
        )
    if problems:
        return None, tuple(problems)

    def _resolve_root(
        *,
        reference: CanonicalReference,
        expected_role: MemberRole,
        label: str,
    ) -> MemberInventoryEntry | None:
        try:
            inventory_entry = claim_record.member_inventory.entry_for_reference(
                canonical_reference=reference
            )
        except MemberError:
            problems.append(
                build_replay_problem(
                    problem_type=MISSING_REQUIRED_ROOT,
                    title="Required root designator is missing.",
                    detail=(
                        f"The claim record does not resolve a {label} root member."
                    ),
                    governing_step=STEP_VERIFY_REQUIRED_ROOTS,
                    related_reference=reference,
                )
            )
            return None
        if inventory_entry.member_role is not expected_role:
            problems.append(
                build_replay_problem(
                    problem_type=MISSING_REQUIRED_ROOT,
                    title="Required root designator resolves to the wrong member role.",
                    detail=(
                        f"The {label} root designator does not resolve to a "
                        f"{expected_role.value} inventory entry."
                    ),
                    governing_step=STEP_VERIFY_REQUIRED_ROOTS,
                    related_reference=reference,
                )
            )
            return None
        return inventory_entry

    judged = _resolve_root(
        reference=claim_record.root_designators.judged_object_carrier_reference,
        expected_role=MemberRole.JUDGED_OBJECT_CARRIER_ROOT,
        label="judged-object",
    )
    evidence = _resolve_root(
        reference=claim_record.root_designators.evidence_state_carrier_reference,
        expected_role=MemberRole.EVIDENCE_STATE_CARRIER_ROOT,
        label="evidence-state",
    )
    evaluator = _resolve_root(
        reference=claim_record.root_designators.evaluator_carrier_reference,
        expected_role=MemberRole.EVALUATOR_CARRIER_ROOT,
        label="evaluator",
    )
    if problems:
        return None, tuple(problems)
    if judged is None or evidence is None or evaluator is None:
        return None, tuple(problems)
    return ValidatedRoots(judged=judged, evidence=evidence, evaluator=evaluator), ()
