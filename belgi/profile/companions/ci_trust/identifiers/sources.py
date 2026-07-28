from __future__ import annotations

from belgi.profile.governance import EvidenceSourceClassId

__all__ = [
    "ALL_SOURCE_MATERIAL_ROLES",
    "ARTIFACT_ORIGIN_RECORD",
    "RUNNER_ENVIRONMENT_RECORD",
    "RUN_ATTESTATION",
    "RUN_RECORD",
    "STATUS_SUMMARY",
    "WORKFLOW_DEFINITION",
]


RUN_RECORD = EvidenceSourceClassId("belgi.ci.source.run-record")
RUN_ATTESTATION = EvidenceSourceClassId("belgi.ci.source.run-attestation")
WORKFLOW_DEFINITION = EvidenceSourceClassId("belgi.ci.source.workflow-definition")
RUNNER_ENVIRONMENT_RECORD = EvidenceSourceClassId(
    "belgi.ci.source.runner-environment-record"
)
ARTIFACT_ORIGIN_RECORD = EvidenceSourceClassId("belgi.ci.source.artifact-origin-record")
STATUS_SUMMARY = EvidenceSourceClassId("belgi.ci.source.status-summary")

ALL_SOURCE_MATERIAL_ROLES: tuple[EvidenceSourceClassId, ...] = (
    RUN_RECORD,
    RUN_ATTESTATION,
    WORKFLOW_DEFINITION,
    RUNNER_ENVIRONMENT_RECORD,
    ARTIFACT_ORIGIN_RECORD,
    STATUS_SUMMARY,
)
