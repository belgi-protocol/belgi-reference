from __future__ import annotations

from belgi.profile.reference_profile.identifiers.conditions import (
    ANALYSIS_POLICY_SATISFIED,
)

from .change_basis import ChangeBasisDeclaration, change_basis_declaration
from .condition import (
    ProfileCondition,
    ProfileConditionDeclaration,
    declared_profile_condition,
)
from .environment import (
    EnvironmentCompatibilityDeclaration,
    EnvironmentRequirement,
    EnvironmentTermValue,
    environment_compatibility_declaration,
)
from .evidence import (
    EvidenceOutcome,
    EvidencePresenceDeclaration,
    RequiredEvidenceBinding,
    evidence_presence_declaration,
)
from .outcome import (
    OutcomePolicyDeclaration,
    analysis_policy_declaration,
    build_policy_declaration,
    coverage_policy_declaration,
    dependency_policy_declaration,
    test_policy_declaration,
)
from .review import ReviewPolicyDeclaration, review_policy_declaration
from .source import (
    ALL_GENERIC_EVIDENCE_SOURCE_CLASSES,
    ARTIFACT_STORE_SOURCE,
    CI_EXECUTION_SOURCE,
    DEPENDENCY_ADVISORY_SERVICE_SOURCE,
    DEVELOPER_WORKSPACE_SOURCE,
    EXTERNAL_ANALYSIS_SERVICE_SOURCE,
    REPOSITORY_SYSTEM_SOURCE,
    REVIEW_SYSTEM_SOURCE,
    SourceBoundaryAssignment,
)

__all__ = [
    "ALL_GENERIC_EVIDENCE_SOURCE_CLASSES",
    "ANALYSIS_POLICY_SATISFIED",
    "ARTIFACT_STORE_SOURCE",
    "CI_EXECUTION_SOURCE",
    "DEPENDENCY_ADVISORY_SERVICE_SOURCE",
    "DEVELOPER_WORKSPACE_SOURCE",
    "EXTERNAL_ANALYSIS_SERVICE_SOURCE",
    "REPOSITORY_SYSTEM_SOURCE",
    "REVIEW_SYSTEM_SOURCE",
    "ChangeBasisDeclaration",
    "EnvironmentCompatibilityDeclaration",
    "EnvironmentRequirement",
    "EnvironmentTermValue",
    "EvidenceOutcome",
    "EvidencePresenceDeclaration",
    "OutcomePolicyDeclaration",
    "ProfileCondition",
    "ProfileConditionDeclaration",
    "RequiredEvidenceBinding",
    "ReviewPolicyDeclaration",
    "SourceBoundaryAssignment",
    "analysis_policy_declaration",
    "build_policy_declaration",
    "change_basis_declaration",
    "coverage_policy_declaration",
    "declared_profile_condition",
    "dependency_policy_declaration",
    "environment_compatibility_declaration",
    "evidence_presence_declaration",
    "review_policy_declaration",
    "test_policy_declaration",
]
