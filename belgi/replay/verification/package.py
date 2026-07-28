"""Replay package-shape verification."""

from __future__ import annotations

from belgi.carrier import ClaimRecord, MemberRole
from belgi.carrier.inventory import MemberError
from belgi.replay.instructions import (
    STEP_VERIFY_CANONICAL_REFERENCE_UNIQUENESS,
    STEP_VERIFY_PACKAGE_CLOSURE,
    STEP_VERIFY_REQUIRED_ROOT_MEMBERS,
)
from belgi.replay.package_source.protocol import ReplayPackageSource
from belgi.replay.problems import (
    DUPLICATE_CANONICAL_REFERENCE,
    MISSING_REQUIRED_MEMBER,
    OUT_OF_CLOSURE_DEPENDENCY,
    UNRESOLVED_DEPENDENCY,
    ReplayProblem,
    build_replay_problem,
)
from belgi.replay.verification.claim_record import ValidatedRoots

__all__ = [
    "validate_canonical_reference_uniqueness",
    "validate_package_closure",
    "validate_root_members_exist",
]


def validate_root_members_exist(
    *,
    package: ReplayPackageSource,
    roots: ValidatedRoots,
) -> tuple[ReplayProblem, ...]:
    problems: list[ReplayProblem] = []
    for inventory_entry, label in (
        (roots.judged, "judged-object"),
        (roots.evidence, "evidence-state"),
        (roots.evaluator, "evaluator"),
    ):
        if package.has_member(inventory_entry=inventory_entry):
            continue
        problems.append(
            build_replay_problem(
                problem_type=MISSING_REQUIRED_MEMBER,
                title="Required root member is missing from the replay package.",
                detail=(
                    f"The claim record designates a {label} root member at "
                    f"{inventory_entry.member_name!s}, but that member is not present in the package."
                ),
                governing_step=STEP_VERIFY_REQUIRED_ROOT_MEMBERS,
                related_reference=inventory_entry.canonical_reference,
            )
        )
    return tuple(problems)


def validate_canonical_reference_uniqueness(
    *,
    claim_record: ClaimRecord,
) -> tuple[ReplayProblem, ...]:
    seen = set()
    problems: list[ReplayProblem] = []
    for inventory_entry in claim_record.member_inventory.replay_relevant_entries():
        reference = inventory_entry.canonical_reference
        if reference is None:
            continue
        if reference not in seen:
            seen.add(reference)
            continue
        problems.append(
            build_replay_problem(
                problem_type=DUPLICATE_CANONICAL_REFERENCE,
                title="Canonical reference is not unique within the replay package.",
                detail=(
                    f"Canonical reference {reference!r} is assigned to more than one "
                    "replay-relevant package member."
                ),
                governing_step=STEP_VERIFY_CANONICAL_REFERENCE_UNIQUENESS,
                related_reference=reference,
            )
        )
    return tuple(problems)


def validate_package_closure(
    *,
    package: ReplayPackageSource,
    claim_record: ClaimRecord,
) -> tuple[ReplayProblem, ...]:
    problems: list[ReplayProblem] = []
    for inventory_entry in claim_record.member_inventory.replay_relevant_entries():
        if inventory_entry.member_role is MemberRole.CLAIM_RECORD:
            continue
        if package.has_member(inventory_entry=inventory_entry):
            continue
        problems.append(
            build_replay_problem(
                problem_type=OUT_OF_CLOSURE_DEPENDENCY,
                title="Replay-relevant member falls outside package closure.",
                detail=(
                    f"The replay-relevant member {inventory_entry.member_name!s} is designated in the "
                    "claim record but is not preserved in the replay package."
                ),
                governing_step=STEP_VERIFY_PACKAGE_CLOSURE,
                related_reference=inventory_entry.canonical_reference,
            )
        )

    for dependency in claim_record.dependency_declarations:
        try:
            dependent_entry = claim_record.member_inventory.entry_for_reference(
                canonical_reference=dependency.dependent_reference
            )
            dependency_entry = claim_record.member_inventory.entry_for_reference(
                canonical_reference=dependency.dependency_reference
            )
        except MemberError:
            problems.append(
                build_replay_problem(
                    problem_type=UNRESOLVED_DEPENDENCY,
                    title="Dependency declaration does not resolve in the package inventory.",
                    detail=(
                        f"Dependency declaration {dependency.dependent_reference!r} -> "
                        f"{dependency.dependency_reference!r} does not resolve fully in the claim record."
                    ),
                    governing_step=STEP_VERIFY_PACKAGE_CLOSURE,
                    related_reference=dependency.dependency_reference,
                )
            )
            continue
        if not package.has_member(inventory_entry=dependent_entry):
            problems.append(
                build_replay_problem(
                    problem_type=OUT_OF_CLOSURE_DEPENDENCY,
                    title="Dependent replay-relevant member is not preserved in the package.",
                    detail=(
                        f"The dependency source member {dependent_entry.member_name!s} is not preserved "
                        "in the replay package."
                    ),
                    governing_step=STEP_VERIFY_PACKAGE_CLOSURE,
                    related_reference=dependency.dependent_reference,
                )
            )
        if not package.has_member(inventory_entry=dependency_entry):
            problems.append(
                build_replay_problem(
                    problem_type=OUT_OF_CLOSURE_DEPENDENCY,
                    title="Dependency target is not preserved in the replay package.",
                    detail=(
                        f"The dependency target member {dependency_entry.member_name!s} is not preserved "
                        "in the replay package."
                    ),
                    governing_step=STEP_VERIFY_PACKAGE_CLOSURE,
                    related_reference=dependency.dependency_reference,
                )
            )
    return tuple(problems)
