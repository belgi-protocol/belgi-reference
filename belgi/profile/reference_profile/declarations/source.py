from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.governance import (
    AuthorityLevelId,
    BoundaryParticipationId,
    EvidenceSourceClassId,
)
from belgi.profile.reference_profile.identifiers.boundary import EXCLUDED, INCLUDED

__all__ = [
    "ALL_GENERIC_EVIDENCE_SOURCE_CLASSES",
    "ARTIFACT_STORE_SOURCE",
    "CI_EXECUTION_SOURCE",
    "DEPENDENCY_ADVISORY_SERVICE_SOURCE",
    "DEVELOPER_WORKSPACE_SOURCE",
    "EXTERNAL_ANALYSIS_SERVICE_SOURCE",
    "REPOSITORY_SYSTEM_SOURCE",
    "REVIEW_SYSTEM_SOURCE",
    "SourceBoundaryAssignment",
]


REPOSITORY_SYSTEM_SOURCE = EvidenceSourceClassId(
    "belgi.software-change.source.repository-system"
)
REVIEW_SYSTEM_SOURCE = EvidenceSourceClassId(
    "belgi.software-change.source.review-system"
)
CI_EXECUTION_SOURCE = EvidenceSourceClassId("belgi.software-change.source.ci-execution")
ARTIFACT_STORE_SOURCE = EvidenceSourceClassId(
    "belgi.software-change.source.artifact-store"
)
DEPENDENCY_ADVISORY_SERVICE_SOURCE = EvidenceSourceClassId(
    "belgi.software-change.source.dependency-advisory-service"
)
DEVELOPER_WORKSPACE_SOURCE = EvidenceSourceClassId(
    "belgi.software-change.source.developer-workspace"
)
EXTERNAL_ANALYSIS_SERVICE_SOURCE = EvidenceSourceClassId(
    "belgi.software-change.source.external-analysis-service"
)

ALL_GENERIC_EVIDENCE_SOURCE_CLASSES: tuple[EvidenceSourceClassId, ...] = (
    REPOSITORY_SYSTEM_SOURCE,
    REVIEW_SYSTEM_SOURCE,
    CI_EXECUTION_SOURCE,
    ARTIFACT_STORE_SOURCE,
    DEPENDENCY_ADVISORY_SERVICE_SOURCE,
    DEVELOPER_WORKSPACE_SOURCE,
    EXTERNAL_ANALYSIS_SERVICE_SOURCE,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class SourceBoundaryAssignment:
    source_class: EvidenceSourceClassId
    boundary_participation: BoundaryParticipationId
    authority_level: AuthorityLevelId | None

    def __post_init__(self) -> None:
        if self.boundary_participation == INCLUDED and self.authority_level is None:
            raise ValueError(
                "included source-boundary assignments require an authority_level."
            )
        if self.boundary_participation == EXCLUDED and self.authority_level is not None:
            raise ValueError(
                "excluded source-boundary assignments must not declare authority_level."
            )
