"""Claim-record read step for replay verification."""

from __future__ import annotations

from belgi.carrier import (
    ClaimRecordBootstrap,
    ClaimRecordError,
    PackageAssemblyError,
    PackageIdentifier,
    parse_claim_record_bootstrap,
)
from belgi.carrier.package.representation.contract import BASELINE_ENVELOPE
from belgi.replay.instructions import STEP_READ_CLAIM_RECORD
from belgi.replay.package_source.exceptions import PackageSourceMemberNotFoundError
from belgi.replay.package_source.protocol import ReplayPackageSource
from belgi.replay.problems import (
    MALFORMED_CLAIM_RECORD,
    ReplayProblem,
    build_replay_problem,
)

__all__ = ["read_claim_record"]


def read_claim_record(
    *,
    package: ReplayPackageSource,
) -> tuple[
    ClaimRecordBootstrap | None,
    bytes | None,
    tuple[ReplayProblem, ...],
    PackageIdentifier | None,
]:
    try:
        claim_record_bytes = package.claim_record_bytes()
        if len(claim_record_bytes) > BASELINE_ENVELOPE.claim_record_bytes:
            raise ClaimRecordError("claim record exceeds its bootstrap byte envelope.")
        bootstrap = parse_claim_record_bootstrap(
            claim_record_bytes=claim_record_bytes,
            maximum_member_count=BASELINE_ENVELOPE.member_count,
            maximum_member_name_octets=BASELINE_ENVELOPE.path_bytes,
        )
        return bootstrap, claim_record_bytes, (), bootstrap.package_identifier
    except (
        ClaimRecordError,
        KeyError,
        OSError,
        PackageAssemblyError,
        PackageSourceMemberNotFoundError,
    ) as exc:
        return (
            None,
            None,
            (
                build_replay_problem(
                    problem_type=MALFORMED_CLAIM_RECORD,
                    title="Claim record could not be read as preserved.",
                    detail=str(exc),
                    governing_step=STEP_READ_CLAIM_RECORD,
                ),
            ),
            None,
        )
