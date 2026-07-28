from __future__ import annotations

from belgi.carrier import (
    PACKAGE_INTEGRITY_ANCHOR_MEDIA_TYPE,
    PACKAGE_INTEGRITY_ANCHOR_SCHEMA_DESIGNATOR,
    PACKAGE_INTEGRITY_MANIFEST_MEDIA_TYPE,
    PACKAGE_INTEGRITY_MANIFEST_SCHEMA_DESIGNATOR,
    CanonicalReference,
    CarrierError,
    ClaimRecordBootstrap,
    ImmutableDesignator,
    MemberClassification,
    MemberName,
    MemberRole,
)
from belgi.carrier.package.names import (
    PACKAGE_INTEGRITY_ANCHOR_MEMBER_NAME,
    PACKAGE_INTEGRITY_MANIFEST_MEMBER_NAME,
)
from belgi.replay.instructions import (
    STEP_VERIFY_CLAIM_RECORD_INTEGRITY_BINDING_PRESENCE,
)
from belgi.replay.package_source.protocol import ReplayPackageSource
from belgi.replay.problems import (
    CLAIM_RECORD_INTEGRITY_BINDING_MISSING,
    ReplayProblem,
    build_replay_problem,
)
from belgi.replay.verification.claim_record.integrity.bootstrap_members import (
    observe_bootstrap_member,
)
from belgi.replay.verification.claim_record.integrity.model import (
    ClaimRecordIntegrityRecovery,
)

__all__ = ["validate_claim_record_integrity_binding_presence"]


def validate_claim_record_integrity_binding_presence(
    *,
    package: ReplayPackageSource,
    bootstrap: ClaimRecordBootstrap,
) -> tuple[ClaimRecordIntegrityRecovery | None, tuple[ReplayProblem, ...]]:
    try:
        claim_member = observe_bootstrap_member(entry=bootstrap.claim_record_entry)
    except CarrierError as exc:
        return None, (
            _binding_missing_problem(
                title="Claim-record inventory binding is inapplicable.",
                detail=str(exc),
                related_reference=None,
            ),
        )
    if (
        claim_member.member_role != MemberRole.CLAIM_RECORD.value
        or claim_member.classification != MemberClassification.REPLAY_RELEVANT.value
        or claim_member.canonical_reference is None
    ):
        return None, (
            _binding_missing_problem(
                title="Claim-record inventory binding is inapplicable.",
                detail=(
                    "The claim-record member shall be replay-relevant, use the "
                    "claim-record role, and preserve a canonical reference."
                ),
                related_reference=claim_member.canonical_reference,
            ),
        )

    manifest_problem = _recovery_member_problem(
        package=package,
        bootstrap=bootstrap,
        member_name=PACKAGE_INTEGRITY_MANIFEST_MEMBER_NAME,
        expected_role=MemberRole.PACKAGE_INTEGRITY_MANIFEST,
        expected_media_type=PACKAGE_INTEGRITY_MANIFEST_MEDIA_TYPE,
        expected_schema=PACKAGE_INTEGRITY_MANIFEST_SCHEMA_DESIGNATOR,
        label="Package-integrity manifest",
        related_reference=claim_member.canonical_reference,
    )
    if manifest_problem is not None:
        return None, (manifest_problem,)
    anchor_problem = _recovery_member_problem(
        package=package,
        bootstrap=bootstrap,
        member_name=PACKAGE_INTEGRITY_ANCHOR_MEMBER_NAME,
        expected_role=MemberRole.PACKAGE_INTEGRITY_ANCHOR,
        expected_media_type=PACKAGE_INTEGRITY_ANCHOR_MEDIA_TYPE,
        expected_schema=PACKAGE_INTEGRITY_ANCHOR_SCHEMA_DESIGNATOR,
        label="Package-integrity anchor",
        related_reference=claim_member.canonical_reference,
    )
    if anchor_problem is not None:
        return None, (anchor_problem,)
    return ClaimRecordIntegrityRecovery(
        claim_record_member_name=MemberName(claim_member.member_name),
        claim_record_reference=claim_member.canonical_reference,
        manifest_member_name=PACKAGE_INTEGRITY_MANIFEST_MEMBER_NAME,
        anchor_member_name=PACKAGE_INTEGRITY_ANCHOR_MEMBER_NAME,
    ), ()


def _recovery_member_problem(
    *,
    package: ReplayPackageSource,
    bootstrap: ClaimRecordBootstrap,
    member_name: MemberName,
    expected_role: MemberRole,
    expected_media_type: str,
    expected_schema: ImmutableDesignator,
    label: str,
    related_reference: CanonicalReference,
) -> ReplayProblem | None:
    entry = bootstrap.entry_for_name(member_name=member_name)
    try:
        member = observe_bootstrap_member(entry=entry)
    except CarrierError as exc:
        return _binding_missing_problem(
            title=f"{label} inventory binding is inapplicable.",
            detail=str(exc),
            related_reference=related_reference,
        )
    if (
        member.member_role != expected_role.value
        or member.classification
        != MemberClassification.CLAIM_RECORD_INTEGRITY_RECOVERY.value
    ):
        return _binding_missing_problem(
            title=f"{label} uses the wrong inventory identity.",
            detail=(
                f"The designated member {member_name!s} shall use role "
                f"{expected_role.value!r} with claim-record-integrity-recovery "
                "classification."
            ),
            related_reference=related_reference,
        )
    if member.media_type != expected_media_type:
        return _binding_missing_problem(
            title=f"{label} uses the wrong representation.",
            detail=(
                f"The designated member {member_name!s} does not preserve "
                f"{expected_media_type!r}."
            ),
            related_reference=related_reference,
        )
    if member.schema_designator != expected_schema:
        return _binding_missing_problem(
            title=f"{label} schema designator is invalid.",
            detail=(
                f"The designated member {member_name!s} does not preserve the "
                f"expected {label.lower()} schema designator."
            ),
            related_reference=related_reference,
        )
    if not package.has_bootstrap_member(member_name=member_name):
        return _binding_missing_problem(
            title=f"{label} is missing from the replay package.",
            detail=(
                f"The fixed {label.lower()} member {member_name!s} is not "
                "preserved in the replay package."
            ),
            related_reference=related_reference,
        )
    return None


def _binding_missing_problem(
    *,
    title: str,
    detail: str,
    related_reference: CanonicalReference | None,
) -> ReplayProblem:
    return build_replay_problem(
        problem_type=CLAIM_RECORD_INTEGRITY_BINDING_MISSING,
        title=title,
        detail=detail,
        governing_step=STEP_VERIFY_CLAIM_RECORD_INTEGRITY_BINDING_PRESENCE,
        related_reference=related_reference,
    )
