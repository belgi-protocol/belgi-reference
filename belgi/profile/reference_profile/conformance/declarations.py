from __future__ import annotations

from belgi.profile.companions.agent_admission.edition import (
    COMPANION_IDENTIFIER as AGENT_ADMISSION_COMPANION_IDENTIFIER,
)
from belgi.profile.companions.agent_admission.edition import (
    COMPANION_VERSION as AGENT_ADMISSION_COMPANION_VERSION,
)
from belgi.profile.edition import ExactEditionBinding

from .model import (
    ReferenceProfileConformanceArtifactSet,
    ReferenceProfileVerdictInteropDeclaration,
)

__all__ = [
    "AGENT_ADMISSION_VERDICT_INTEROP_PACKAGE_CLASS",
    "reference_profile_agent_admission_verdict_interop_declaration",
]


AGENT_ADMISSION_VERDICT_INTEROP_PACKAGE_CLASS = (
    "belgi.reference-profile.conformance.agent-admission-verdict-interop"
)


def reference_profile_agent_admission_verdict_interop_declaration(
    *,
    agent_admission_companion: ExactEditionBinding,
    supporting_companions: tuple[ExactEditionBinding, ...] = (),
    conformance_artifacts: ReferenceProfileConformanceArtifactSet,
) -> ReferenceProfileVerdictInteropDeclaration:
    if not _reference_profile_conformance_agent_admission_binding(
        binding=agent_admission_companion,
    ):
        raise ValueError(
            "agent_admission_companion must select the agent-admission companion exact edition."
        )
    return ReferenceProfileVerdictInteropDeclaration(
        package_class_identifier=AGENT_ADMISSION_VERDICT_INTEROP_PACKAGE_CLASS,
        agent_admission_companion=agent_admission_companion,
        supporting_companions=tuple(dict.fromkeys(supporting_companions)),
        conformance_artifacts=conformance_artifacts,
    )


def _reference_profile_conformance_agent_admission_binding(
    *,
    binding: ExactEditionBinding,
) -> bool:
    return str(binding.family_identifier) == str(
        AGENT_ADMISSION_COMPANION_IDENTIFIER
    ) and str(binding.version_designator) == str(AGENT_ADMISSION_COMPANION_VERSION)
