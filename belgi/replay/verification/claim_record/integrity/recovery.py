from __future__ import annotations

from belgi.carrier import (
    CanonicalReference,
    ClaimRecordBootstrap,
    PackageAssemblyError,
    PackageIntegrityAnchor,
    PackageIntegrityManifest,
    PackageIntegrityManifestError,
    parse_package_integrity_manifest_bytes,
)
from belgi.replay.context import PackageIntegrityAnchorVerifier
from belgi.replay.instructions import STEP_VERIFY_CLAIM_RECORD_INTEGRITY
from belgi.replay.package_source.exceptions import PackageSourceMemberNotFoundError
from belgi.replay.package_source.protocol import ReplayPackageSource
from belgi.replay.problems import (
    CLAIM_RECORD_INTEGRITY_BINDING_MISMATCH,
    CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
    CLAIM_RECORD_INTEGRITY_RECOVERY_MALFORMED,
    ReplayProblem,
    build_replay_problem,
)
from belgi.replay.verification.claim_record.integrity.model import (
    ClaimRecordIntegrityRecovery,
)
from belgi.replay.verification.integrity import verify_package_integrity_anchor

__all__ = [
    "claim_record_integrity_problem",
    "recover_claim_record_integrity_manifest",
]

_VERIFICATION_FAILURE_KIND_TO_PROBLEM_TYPE = {
    "binding-mismatch": CLAIM_RECORD_INTEGRITY_BINDING_MISMATCH,
    "recovery-failure": CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
    "recovery-malformed": CLAIM_RECORD_INTEGRITY_RECOVERY_MALFORMED,
}


def claim_record_integrity_problem(
    *,
    problem_type,
    title: str,
    detail: str,
    related_reference: CanonicalReference | None,
    procedure_substep: str,
) -> ReplayProblem:
    return build_replay_problem(
        problem_type=problem_type,
        title=title,
        detail=detail,
        governing_step=STEP_VERIFY_CLAIM_RECORD_INTEGRITY,
        related_reference=related_reference,
        procedure_substep=procedure_substep,
    )


def recover_claim_record_integrity_manifest(
    *,
    package: ReplayPackageSource,
    bootstrap: ClaimRecordBootstrap,
    claim_record_bytes: bytes,
    claim_record_reference: CanonicalReference,
    recovery: ClaimRecordIntegrityRecovery,
    package_integrity_anchor_verifier: PackageIntegrityAnchorVerifier,
) -> tuple[
    PackageIntegrityManifest | None,
    PackageIntegrityAnchor | None,
    tuple[ReplayProblem, ...],
]:
    try:
        observed_claim_record_bytes = package.read_bootstrap_member(
            member_name=recovery.claim_record_member_name
        )
    except (
        KeyError,
        OSError,
        PackageAssemblyError,
        PackageSourceMemberNotFoundError,
    ) as exc:
        return (
            None,
            None,
            (
                claim_record_integrity_problem(
                    problem_type=CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
                    title="Claim-record member could not be recovered.",
                    detail=str(exc),
                    related_reference=claim_record_reference,
                    procedure_substep="3a",
                ),
            ),
        )
    if observed_claim_record_bytes != claim_record_bytes:
        return (
            None,
            None,
            (
                claim_record_integrity_problem(
                    problem_type=CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
                    title="Claim-record byte authority is inconsistent.",
                    detail=(
                        "Replay package exposes claim-record bytes that do not "
                        "match the preserved bytes of the designated claim-record member."
                    ),
                    related_reference=claim_record_reference,
                    procedure_substep="3a",
                ),
            ),
        )
    try:
        manifest_bytes = package.read_bootstrap_member(
            member_name=recovery.manifest_member_name
        )
    except (
        KeyError,
        OSError,
        PackageAssemblyError,
        PackageSourceMemberNotFoundError,
    ) as exc:
        return (
            None,
            None,
            (
                claim_record_integrity_problem(
                    problem_type=CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
                    title="Package-integrity manifest could not be read.",
                    detail=str(exc),
                    related_reference=claim_record_reference,
                    procedure_substep="3a",
                ),
            ),
        )
    try:
        anchor_bytes = package.read_bootstrap_member(
            member_name=recovery.anchor_member_name
        )
    except (
        KeyError,
        OSError,
        PackageAssemblyError,
        PackageSourceMemberNotFoundError,
    ) as exc:
        return (
            None,
            None,
            (
                claim_record_integrity_problem(
                    problem_type=CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
                    title="Package-integrity anchor could not be read.",
                    detail=str(exc),
                    related_reference=claim_record_reference,
                    procedure_substep="3a",
                ),
            ),
        )
    anchor, verification_error = verify_package_integrity_anchor(
        anchor_bytes=anchor_bytes,
        manifest_bytes=manifest_bytes,
        verifier=package_integrity_anchor_verifier,
    )
    if verification_error is not None:
        failure_kind, title, detail = verification_error
        return (
            None,
            None,
            (
                claim_record_integrity_problem(
                    problem_type=_VERIFICATION_FAILURE_KIND_TO_PROBLEM_TYPE.get(
                        failure_kind,
                        CLAIM_RECORD_INTEGRITY_RECOVERY_FAILURE,
                    ),
                    title=title,
                    detail=detail,
                    related_reference=claim_record_reference,
                    procedure_substep="3a",
                ),
            ),
        )
    try:
        manifest = parse_package_integrity_manifest_bytes(
            preserved_bytes=manifest_bytes,
        )
    except PackageIntegrityManifestError as exc:
        return (
            None,
            None,
            (
                claim_record_integrity_problem(
                    problem_type=CLAIM_RECORD_INTEGRITY_RECOVERY_MALFORMED,
                    title="Package-integrity manifest is malformed.",
                    detail=str(exc),
                    related_reference=claim_record_reference,
                    procedure_substep="3b",
                ),
            ),
        )
    if anchor is None:
        raise RuntimeError("Successful anchor verification returned no parsed anchor.")
    return manifest, anchor, ()
