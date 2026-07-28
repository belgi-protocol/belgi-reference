from __future__ import annotations

from dataclasses import dataclass

from belgi.carrier import (
    ClaimRecord,
    ClaimRecordError,
    PackageIdentifier,
    PackageIntegrityManifest,
    parse_claim_record_bytes_for_replay_read,
)
from belgi.replay.context import PackageIntegrityAnchorVerifier
from belgi.replay.instructions import (
    STEP_VALIDATE_AUTHENTICATED_CLAIM_RECORD,
)
from belgi.replay.package_representation.model import RepresentationResult
from belgi.replay.package_source.protocol import (
    PhysicalReplayPackageSource,
    ReplayPackageSource,
)
from belgi.replay.package_source.recovery import require_source_recovery_bindings
from belgi.replay.problems import (
    MALFORMED_CLAIM_RECORD,
    ReplayProblem,
    build_replay_problem,
)
from belgi.replay.verification.claim_record.integrity.presence import (
    validate_claim_record_integrity_binding_presence,
)
from belgi.replay.verification.claim_record.integrity.verification import (
    validate_claim_record_integrity,
)
from belgi.replay.verification.claim_record.read import read_claim_record
from belgi.replay.verification.claim_record.required_roots import (
    ValidatedRoots,
    validate_required_roots,
)
from belgi.replay.verification.integrity import (
    validate_integrity_binding_presence,
    validate_integrity_bindings,
)
from belgi.replay.verification.package import (
    validate_canonical_reference_uniqueness,
    validate_package_closure,
    validate_root_members_exist,
)

__all__ = ["ReplayPackageVerification", "verify_replay_package"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplayPackageVerification:
    package_identifier: PackageIdentifier | None
    claim_record: ClaimRecord | None
    roots: ValidatedRoots | None
    package_integrity_manifest: PackageIntegrityManifest | None
    representation_result: RepresentationResult | None
    problems: tuple[ReplayProblem, ...]

    @property
    def successful(self) -> bool:
        return not self.problems


def verify_replay_package(
    *,
    package: ReplayPackageSource,
    package_integrity_anchor_verifier: PackageIntegrityAnchorVerifier,
) -> ReplayPackageVerification:
    bootstrap, claim_record_bytes, problems, package_identifier = read_claim_record(
        package=package
    )
    if problems:
        return _failed_verification(
            package_identifier=package_identifier,
            claim_record=None,
            problems=problems,
        )
    if bootstrap is None or claim_record_bytes is None or package_identifier is None:
        raise RuntimeError(
            "Replay procedure expected a claim record, preserved bytes, and package "
            "identifier after successful step 1."
        )

    recovery, problems = validate_claim_record_integrity_binding_presence(
        package=package,
        bootstrap=bootstrap,
    )
    if problems:
        return _failed_verification(
            package_identifier=package_identifier,
            claim_record=None,
            problems=problems,
        )
    if recovery is None:
        raise RuntimeError(
            "Replay procedure expected a claim-record integrity recovery branch "
            "after successful step 2."
        )

    package_integrity_manifest, problems = validate_claim_record_integrity(
        package=package,
        bootstrap=bootstrap,
        claim_record_bytes=claim_record_bytes,
        recovery=recovery,
        package_integrity_anchor_verifier=package_integrity_anchor_verifier,
    )
    if problems:
        return _failed_verification(
            package_identifier=package_identifier,
            claim_record=None,
            problems=problems,
        )
    if package_integrity_manifest is None:
        raise RuntimeError(
            "Replay procedure expected one package-integrity manifest after "
            "successful step 3."
        )

    try:
        claim_record = parse_claim_record_bytes_for_replay_read(
            claim_record_bytes=claim_record_bytes,
        )
    except ClaimRecordError as exc:
        return _failed_verification(
            package_identifier=package_identifier,
            claim_record=None,
            problems=(
                build_replay_problem(
                    problem_type=MALFORMED_CLAIM_RECORD,
                    title="Authenticated claim record is malformed.",
                    detail=str(exc),
                    governing_step=STEP_VALIDATE_AUTHENTICATED_CLAIM_RECORD,
                ),
            ),
        )

    representation_result = None
    if isinstance(package, PhysicalReplayPackageSource):
        representation_result = require_source_recovery_bindings(
            package,
            claim_record=claim_record,
        )

    roots, problems = validate_required_roots(claim_record=claim_record)
    if problems:
        return _failed_verification(
            package_identifier=package_identifier,
            claim_record=claim_record,
            representation_result=representation_result,
            problems=problems,
        )
    if roots is None:
        raise RuntimeError(
            "Replay procedure expected validated roots after successful step 4."
        )

    verification_steps = (
        lambda: validate_root_members_exist(package=package, roots=roots),
        lambda: validate_canonical_reference_uniqueness(claim_record=claim_record),
        lambda: validate_package_closure(package=package, claim_record=claim_record),
        lambda: validate_integrity_binding_presence(
            claim_record=claim_record,
            package_integrity_manifest=package_integrity_manifest,
        ),
        lambda: validate_integrity_bindings(
            package=package,
            claim_record=claim_record,
            package_integrity_manifest=package_integrity_manifest,
            package_integrity_anchor_verifier=package_integrity_anchor_verifier,
        ),
    )
    for verification_step in verification_steps:
        step_problems = verification_step()
        if step_problems:
            return _failed_verification(
                package_identifier=package_identifier,
                claim_record=claim_record,
                representation_result=representation_result,
                problems=step_problems,
            )
    return ReplayPackageVerification(
        package_identifier=package_identifier,
        claim_record=claim_record,
        roots=roots,
        package_integrity_manifest=package_integrity_manifest,
        representation_result=representation_result,
        problems=(),
    )


def _failed_verification(
    *,
    package_identifier: PackageIdentifier | None,
    claim_record: ClaimRecord | None,
    representation_result: RepresentationResult | None = None,
    problems: tuple[ReplayProblem, ...],
) -> ReplayPackageVerification:
    return ReplayPackageVerification(
        package_identifier=package_identifier,
        claim_record=claim_record,
        roots=None,
        package_integrity_manifest=None,
        representation_result=representation_result,
        problems=problems,
    )
