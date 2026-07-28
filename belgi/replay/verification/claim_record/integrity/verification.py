from __future__ import annotations

from belgi.carrier import (
    BoundObjectKind,
    CanonicalReference,
    ClaimRecordBootstrap,
    PackageIntegrityManifest,
    PackageIntegrityManifestError,
)
from belgi.replay.context import PackageIntegrityAnchorVerifier
from belgi.replay.package_source.protocol import ReplayPackageSource
from belgi.replay.problems import (
    CLAIM_RECORD_INTEGRITY_BINDING_MISMATCH,
    CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
    ReplayProblem,
)
from belgi.replay.verification.claim_record.integrity.cross_binding import (
    IntegrityTargetBindings,
    integrity_target_bindings_match,
)
from belgi.replay.verification.claim_record.integrity.model import (
    ClaimRecordIntegrityRecovery,
)
from belgi.replay.verification.claim_record.integrity.recovery import (
    claim_record_integrity_problem,
    recover_claim_record_integrity_manifest,
)
from belgi.replay.verification.rule_source import validate_selected_digest_rule
from belgi.substrate.hash import sha256_bytes

__all__ = ["validate_claim_record_integrity"]


def validate_claim_record_integrity(
    *,
    package: ReplayPackageSource,
    bootstrap: ClaimRecordBootstrap,
    claim_record_bytes: bytes,
    recovery: ClaimRecordIntegrityRecovery,
    package_integrity_anchor_verifier: PackageIntegrityAnchorVerifier,
) -> tuple[PackageIntegrityManifest | None, tuple[ReplayProblem, ...]]:
    if bootstrap.preserved_claim_record_bytes != claim_record_bytes:
        raise RuntimeError(
            "Replay procedure changed the immutable step-1 claim-record snapshot."
        )
    verified_claim_record_reference: CanonicalReference = (
        recovery.claim_record_reference
    )
    manifest, anchor, problems = recover_claim_record_integrity_manifest(
        package=package,
        bootstrap=bootstrap,
        claim_record_bytes=claim_record_bytes,
        claim_record_reference=verified_claim_record_reference,
        recovery=recovery,
        package_integrity_anchor_verifier=package_integrity_anchor_verifier,
    )
    if problems:
        return None, problems
    if manifest is None or anchor is None:
        raise RuntimeError(
            "Claim-record integrity recovery returned incomplete authenticated state."
        )
    try:
        integrity_binding = manifest.binding_for_reference(
            canonical_reference=verified_claim_record_reference,
        )
    except PackageIntegrityManifestError as exc:
        return None, (
            claim_record_integrity_problem(
                problem_type=CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
                title="Claim-record integrity binding is unavailable.",
                detail=str(exc),
                related_reference=verified_claim_record_reference,
                procedure_substep="3c",
            ),
        )
    if integrity_binding.member_reference != verified_claim_record_reference:
        return None, (
            claim_record_integrity_problem(
                problem_type=CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
                title="Claim-record integrity binding targets the wrong member.",
                detail=(
                    "Claim-record integrity binding member reference does not match "
                    "the claim-record canonical reference."
                ),
                related_reference=verified_claim_record_reference,
                procedure_substep="3c",
            ),
        )
    if not validate_selected_digest_rule(
        identifier=integrity_binding.algorithm_identifier,
        designator=integrity_binding.algorithm_designator,
        support=package_integrity_anchor_verifier,
    ).accepted:
        return None, (
            claim_record_integrity_problem(
                problem_type=CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
                title="Claim-record integrity algorithm is unsupported.",
                detail=(
                    "Claim-record integrity requires the independently selected "
                    "source-bound SHA-256 designator."
                ),
                related_reference=verified_claim_record_reference,
                procedure_substep="3c",
            ),
        )
    if integrity_binding.bound_object != BoundObjectKind.EXACT_PRESERVED_OCTETS:
        return None, (
            claim_record_integrity_problem(
                problem_type=CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
                title="Claim-record integrity binding covers the wrong bound object.",
                detail="Claim-record integrity shall bind exact preserved octets.",
                related_reference=verified_claim_record_reference,
                procedure_substep="3c",
            ),
        )
    if sha256_bytes(claim_record_bytes) != integrity_binding.bound_value_hex:
        return None, (
            claim_record_integrity_problem(
                problem_type=CLAIM_RECORD_INTEGRITY_BINDING_MISMATCH,
                title="Claim-record integrity verification failed.",
                detail="Claim-record integrity digest mismatch.",
                related_reference=verified_claim_record_reference,
                procedure_substep="3c",
            ),
        )
    if not integrity_target_bindings_match(
        bindings=IntegrityTargetBindings(
            claim_package_identifier=bootstrap.package_identifier,
            claim_manifest_member_name=(
                bootstrap.package_integrity_manifest_member_name
            ),
            anchor_package_identifier=anchor.package_identifier,
            anchor_manifest_member_name=(anchor.package_integrity_manifest_member_name),
            consumed_manifest_member_name=recovery.manifest_member_name,
        )
    ):
        return None, (
            claim_record_integrity_problem(
                problem_type=CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
                title="Claim-record integrity target cross-binding failed.",
                detail=(
                    "The authenticated claim record, verified anchor, and consumed "
                    "manifest member do not preserve the same package target."
                ),
                related_reference=verified_claim_record_reference,
                procedure_substep="3d",
            ),
        )
    return manifest, ()
