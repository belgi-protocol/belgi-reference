from __future__ import annotations

from belgi.profile.governance import EnvironmentTermId

__all__ = [
    "ALL_ENVIRONMENT_TERMS",
    "CONFIGURATION_INPUT_IDENTITY",
    "DEPENDENCY_STATE_IDENTITY",
    "EXECUTION_ENVIRONMENT_IDENTITY",
    "PLATFORM_IDENTITY",
    "REPOSITORY_IDENTITY",
    "TOOLCHAIN_IDENTITY",
]


REPOSITORY_IDENTITY = EnvironmentTermId(
    "belgi.software-change.environment.repository-identity"
)
EXECUTION_ENVIRONMENT_IDENTITY = EnvironmentTermId(
    "belgi.software-change.environment.execution-environment-identity"
)
PLATFORM_IDENTITY = EnvironmentTermId(
    "belgi.software-change.environment.platform-identity"
)
TOOLCHAIN_IDENTITY = EnvironmentTermId(
    "belgi.software-change.environment.toolchain-identity"
)
DEPENDENCY_STATE_IDENTITY = EnvironmentTermId(
    "belgi.software-change.environment.dependency-state-identity"
)
CONFIGURATION_INPUT_IDENTITY = EnvironmentTermId(
    "belgi.software-change.environment.configuration-input-identity"
)

ALL_ENVIRONMENT_TERMS: tuple[EnvironmentTermId, ...] = (
    REPOSITORY_IDENTITY,
    EXECUTION_ENVIRONMENT_IDENTITY,
    PLATFORM_IDENTITY,
    TOOLCHAIN_IDENTITY,
    DEPENDENCY_STATE_IDENTITY,
    CONFIGURATION_INPUT_IDENTITY,
)
