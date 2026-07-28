from __future__ import annotations

from belgi.profile.governance import EnvironmentTermId

__all__ = [
    "ALL_ENVIRONMENT_TERMS",
    "RUNNER_IMAGE_IDENTITY",
    "RUNNER_PLATFORM_IDENTITY",
    "RUN_IDENTITY",
    "SOURCE_REFERENCE_IDENTITY",
    "TOOLCHAIN_STATE_IDENTITY",
    "TRIGGER_CONTEXT_IDENTITY",
    "WORKFLOW_DEFINITION_IDENTITY",
]


RUN_IDENTITY = EnvironmentTermId("belgi.ci.environment.run-identity")
WORKFLOW_DEFINITION_IDENTITY = EnvironmentTermId(
    "belgi.ci.environment.workflow-definition-identity"
)
SOURCE_REFERENCE_IDENTITY = EnvironmentTermId(
    "belgi.ci.environment.source-reference-identity"
)
RUNNER_PLATFORM_IDENTITY = EnvironmentTermId(
    "belgi.ci.environment.runner-platform-identity"
)
RUNNER_IMAGE_IDENTITY = EnvironmentTermId("belgi.ci.environment.runner-image-identity")
TOOLCHAIN_STATE_IDENTITY = EnvironmentTermId(
    "belgi.ci.environment.toolchain-state-identity"
)
TRIGGER_CONTEXT_IDENTITY = EnvironmentTermId(
    "belgi.ci.environment.trigger-context-identity"
)

ALL_ENVIRONMENT_TERMS: tuple[EnvironmentTermId, ...] = (
    RUN_IDENTITY,
    WORKFLOW_DEFINITION_IDENTITY,
    SOURCE_REFERENCE_IDENTITY,
    RUNNER_PLATFORM_IDENTITY,
    RUNNER_IMAGE_IDENTITY,
    TOOLCHAIN_STATE_IDENTITY,
    TRIGGER_CONTEXT_IDENTITY,
)
