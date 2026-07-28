"""Replay package-integrity verification."""

from __future__ import annotations

from belgi.carrier import (
    BoundObjectKind,
    ClaimRecord,
    IntegrityBinding,
    MemberInventoryEntry,
    MemberRole,
    PackageIntegrityAnchor,
    PackageIntegrityAnchorError,
    PackageIntegrityManifest,
    PackageIntegrityManifestError,
    PackageMember,
    ProjectionMode,
    parse_package_integrity_anchor_bootstrap_bytes,
    parse_package_integrity_anchor_bytes,
)
from belgi.replay.context import PackageIntegrityAnchorVerifier
from belgi.replay.instructions import (
    STEP_VERIFY_INTEGRITY_BINDING_PRESENCE,
    STEP_VERIFY_INTEGRITY_BINDINGS,
)
from belgi.replay.lifting.exceptions import IntegrityVerificationError
from belgi.replay.package_source.protocol import ReplayPackageSource
from belgi.replay.problems import (
    INTEGRITY_BINDING_MISMATCH,
    INTEGRITY_BINDING_MISSING,
    INTEGRITY_BINDING_SOURCE_FAILURE,
    ReplayProblem,
    build_replay_problem,
)
from belgi.replay.verification.rule_source import validate_selected_digest_rule
from belgi.substrate.hash import sha256_bytes

__all__ = [
    "bound_octets_for_integrity",
    "validate_integrity_binding_presence",
    "validate_integrity_bindings",
    "verify_package_integrity_anchor",
]

_PackageIntegrityAnchorVerificationError = tuple[str, str, str]

_MALFORMED_VERIFICATION_CODES = frozenset(
    {
        "key-designator-malformed",
        "key-malformed",
        "signature-malformed",
    }
)
_BINDING_MISMATCH_VERIFICATION_CODES = frozenset(
    {
        "key-binding-mismatch",
        "signature-invalid",
    }
)


def validate_integrity_binding_presence(
    *,
    claim_record: ClaimRecord,
    package_integrity_manifest: PackageIntegrityManifest,
) -> tuple[ReplayProblem, ...]:
    problems: list[ReplayProblem] = []
    for inventory_entry in claim_record.member_inventory.replay_relevant_entries():
        if inventory_entry.member_role is MemberRole.CLAIM_RECORD:
            continue
        if inventory_entry.canonical_reference is None:
            continue
        try:
            package_integrity_manifest.binding_for_reference(
                canonical_reference=inventory_entry.canonical_reference,
            )
        except PackageIntegrityManifestError:
            problems.append(
                build_replay_problem(
                    problem_type=INTEGRITY_BINDING_MISSING,
                    title="Integrity binding is missing.",
                    detail=(
                        "The replay-relevant member "
                        f"{inventory_entry.member_name!s} has no "
                        "package-integrity manifest binding."
                    ),
                    governing_step=STEP_VERIFY_INTEGRITY_BINDING_PRESENCE,
                    related_reference=inventory_entry.canonical_reference,
                )
            )
    return tuple(problems)


def bound_octets_for_integrity(
    *,
    package_member: PackageMember,
    integrity_binding: IntegrityBinding,
) -> bytes:
    projection = package_member.projection
    if projection is None:
        raise IntegrityVerificationError(
            "Replay-relevant package members require a preserved projection."
        )
    if (
        projection.projection_mode is not ProjectionMode.EXACT_PRESERVED_OCTETS
        or projection.projection_rule_designator is not None
    ):
        raise IntegrityVerificationError(
            "Replay only supports exact-preserved-octets replay-relevant projections."
        )
    if integrity_binding.bound_object == BoundObjectKind.EXACT_PRESERVED_OCTETS:
        return package_member.preserved_bytes
    raise IntegrityVerificationError(
        "Replay supports only source-bound exact-preserved-octets integrity bindings."
    )


def validate_integrity_bindings(
    *,
    package: ReplayPackageSource,
    claim_record: ClaimRecord,
    package_integrity_manifest: PackageIntegrityManifest,
    package_integrity_anchor_verifier: PackageIntegrityAnchorVerifier,
) -> tuple[ReplayProblem, ...]:
    entries = tuple(
        sorted(
            (
                entry
                for entry in claim_record.member_inventory.replay_relevant_entries()
                if entry.member_role is not MemberRole.CLAIM_RECORD
                and entry.canonical_reference is not None
                and package.has_member(inventory_entry=entry)
            ),
            key=lambda entry: str(entry.member_name).encode("utf-8"),
        )
    )
    source_problems: list[ReplayProblem] = []
    for inventory_entry in entries:
        canonical_reference = inventory_entry.canonical_reference
        if canonical_reference is None:
            raise IntegrityVerificationError(
                "Replay-relevant integrity entry has no canonical reference."
            )
        integrity_binding = package_integrity_manifest.binding_for_reference(
            canonical_reference=canonical_reference,
        )
        digest_selected = validate_selected_digest_rule(
            identifier=integrity_binding.algorithm_identifier,
            designator=integrity_binding.algorithm_designator,
            support=package_integrity_anchor_verifier,
        ).accepted
        exact_projection_selected = (
            inventory_entry.projection_rule_identifier is None
            and inventory_entry.projection_rule_designator is None
        )
        exact_binding_selected = (
            integrity_binding.bound_object is BoundObjectKind.EXACT_PRESERVED_OCTETS
            and integrity_binding.canonicalization_rule_identifier is None
            and integrity_binding.canonicalization_rule_designator is None
        )
        if not (
            digest_selected and exact_projection_selected and exact_binding_selected
        ):
            source_problems.append(
                _integrity_problem(
                    problem_type=INTEGRITY_BINDING_SOURCE_FAILURE,
                    inventory_entry=inventory_entry,
                    detail=(
                        "An applicable digest, projection, or canonicalization "
                        "identifier/designator pair is not independently supported."
                    ),
                )
            )
    if source_problems:
        return tuple(source_problems)

    problems: list[ReplayProblem] = []
    for inventory_entry in entries:
        canonical_reference = inventory_entry.canonical_reference
        if canonical_reference is None:
            raise IntegrityVerificationError(
                "Replay-relevant integrity entry has no canonical reference."
            )
        integrity_binding = package_integrity_manifest.binding_for_reference(
            canonical_reference=canonical_reference,
        )
        if integrity_binding.member_reference != canonical_reference:
            problems.append(
                _integrity_problem(
                    problem_type=INTEGRITY_BINDING_MISMATCH,
                    inventory_entry=inventory_entry,
                    detail="Integrity binding targets another canonical reference.",
                )
            )
            continue
        package_member = package.package_member(inventory_entry=inventory_entry)
        try:
            bound_octets = bound_octets_for_integrity(
                package_member=package_member,
                integrity_binding=integrity_binding,
            )
        except IntegrityVerificationError as exc:
            problems.append(
                _integrity_problem(
                    problem_type=INTEGRITY_BINDING_MISMATCH,
                    inventory_entry=inventory_entry,
                    detail=str(exc),
                )
            )
            continue
        actual_digest = sha256_bytes(bound_octets)
        if actual_digest != integrity_binding.bound_value_hex:
            problems.append(
                _integrity_problem(
                    problem_type=INTEGRITY_BINDING_MISMATCH,
                    inventory_entry=inventory_entry,
                    detail="Integrity digest mismatch.",
                )
            )
    return tuple(problems)


def _integrity_problem(
    *,
    problem_type,
    inventory_entry: MemberInventoryEntry,
    detail: str,
) -> ReplayProblem:
    return build_replay_problem(
        problem_type=problem_type,
        title="Integrity binding verification failed.",
        detail=f"Member {inventory_entry.member_name!s} failed: {detail}",
        governing_step=STEP_VERIFY_INTEGRITY_BINDINGS,
        related_reference=inventory_entry.canonical_reference,
    )


def verify_package_integrity_anchor(
    *,
    anchor_bytes: bytes,
    manifest_bytes: bytes,
    verifier: PackageIntegrityAnchorVerifier,
) -> tuple[
    PackageIntegrityAnchor | None,
    _PackageIntegrityAnchorVerificationError | None,
]:
    try:
        bootstrap_anchor = parse_package_integrity_anchor_bootstrap_bytes(
            preserved_bytes=anchor_bytes
        )
    except PackageIntegrityAnchorError as exc:
        return None, (
            "recovery-malformed",
            "Package-integrity anchor is malformed.",
            str(exc),
        )
    selection = verifier.select(anchor=bootstrap_anchor)
    if not selection.accepted:
        return None, (
            "recovery-failure",
            "Package-integrity anchor verification failed.",
            selection.detail,
        )
    try:
        anchor = parse_package_integrity_anchor_bytes(preserved_bytes=anchor_bytes)
    except PackageIntegrityAnchorError as exc:
        return None, (
            "recovery-malformed",
            "Package-integrity anchor is malformed.",
            str(exc),
        )
    outcome = verifier(anchor=anchor, manifest_bytes=manifest_bytes)
    if outcome.accepted:
        return anchor, None
    if outcome.code in _MALFORMED_VERIFICATION_CODES:
        failure_kind = "recovery-malformed"
    elif outcome.code in _BINDING_MISMATCH_VERIFICATION_CODES:
        failure_kind = "binding-mismatch"
    else:
        failure_kind = "recovery-failure"
    return None, (
        failure_kind,
        "Package-integrity anchor verification failed.",
        outcome.detail,
    )
