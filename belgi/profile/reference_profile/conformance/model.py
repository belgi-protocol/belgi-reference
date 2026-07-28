from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.edition import ExactEditionBinding
from belgi.profile.governance import DependencyReference

__all__ = [
    "ReferenceProfileConformanceArtifactSet",
    "ReferenceProfileVerdictInteropDeclaration",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileConformanceArtifactSet:
    verdict_interoperability_corpus: DependencyReference
    verdict_interoperability_procedure: DependencyReference


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileVerdictInteropDeclaration:
    package_class_identifier: str
    agent_admission_companion: ExactEditionBinding
    supporting_companions: tuple[ExactEditionBinding, ...]
    conformance_artifacts: ReferenceProfileConformanceArtifactSet

    def __post_init__(self) -> None:
        if not self.package_class_identifier:
            raise ValueError("package_class_identifier must not be empty.")
        if not self.conformance_artifacts.verdict_interoperability_corpus.replay_relevant:
            raise ValueError("verdict_interoperability_corpus must be replay relevant.")
        if not self.conformance_artifacts.verdict_interoperability_procedure.replay_relevant:
            raise ValueError(
                "verdict_interoperability_procedure must be replay relevant."
            )
