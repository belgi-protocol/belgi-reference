from __future__ import annotations

from dataclasses import dataclass

from belgi.profile.companions.agent_admission.edition import (
    COMPANION_IDENTIFIER as AGENT_ADMISSION_COMPANION_IDENTIFIER,
)
from belgi.profile.companions.agent_admission.identifiers import (
    ALL_EVIDENCE_KINDS as AGENT_ADMISSION_EVIDENCE_KINDS,
)
from belgi.profile.companions.python.edition import (
    COMPANION_IDENTIFIER as PYTHON_COMPANION_IDENTIFIER,
)
from belgi.profile.companions.python.identifiers import (
    ALL_EVIDENCE_KINDS as PYTHON_EVIDENCE_KINDS,
)
from belgi.profile.edition import ExactEditionBinding
from belgi.profile.reference_profile.config.exact_editions import (
    resolve_reference_profile_companion_binding,
    resolve_reference_profile_edition_binding,
)
from belgi.profile.reference_profile.identifiers.evidence_kinds import (
    ALL_EVIDENCE_KINDS as REFERENCE_PROFILE_EVIDENCE_KINDS,
)

__all__ = [
    "EvidenceKindOwnerBinding",
    "EvidenceKindOwnershipRegistry",
    "reference_profile_evidence_kind_ownership_registry",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceKindOwnerBinding:
    evidence_kind_identifier: str
    owner: ExactEditionBinding

    def __post_init__(self) -> None:
        if not self.evidence_kind_identifier:
            raise ValueError("evidence-kind owner identifier must be non-empty.")


@dataclass(frozen=True, slots=True, kw_only=True)
class EvidenceKindOwnershipRegistry:
    bindings: tuple[EvidenceKindOwnerBinding, ...]

    def __post_init__(self) -> None:
        observed: dict[str, ExactEditionBinding] = {}
        for binding in self.bindings:
            identifier = binding.evidence_kind_identifier
            if identifier in observed:
                raise ValueError(
                    f"duplicate exact evidence-kind owner binding: {identifier!r}."
                )
            observed[identifier] = binding.owner
        for binding in _built_in_evidence_kind_owner_bindings():
            observed_owner = observed.get(binding.evidence_kind_identifier)
            if observed_owner is None:
                raise ValueError(
                    "evidence-kind registry omitted sealed built-in owner binding: "
                    f"{binding.evidence_kind_identifier!r}."
                )
            if observed_owner != binding.owner:
                raise ValueError(
                    "evidence-kind registry rebound sealed built-in owner binding: "
                    f"{binding.evidence_kind_identifier!r}."
                )

    def owner_for(self, *, evidence_kind_identifier: str) -> ExactEditionBinding | None:
        return next(
            (
                binding.owner
                for binding in self.bindings
                if binding.evidence_kind_identifier == evidence_kind_identifier
            ),
            None,
        )

    def require_owner(self, *, evidence_kind_identifier: str) -> ExactEditionBinding:
        owner = self.owner_for(evidence_kind_identifier=evidence_kind_identifier)
        if owner is None:
            raise ValueError(
                "evidence kind has no exact owner in the selected reference-profile "
                f"surface: {evidence_kind_identifier!r}."
            )
        return owner

    def declared_owners(
        self, *, evidence_kind_identifiers: tuple[str, ...]
    ) -> tuple[ExactEditionBinding, ...]:
        """Return known declared owners; unknown tokens remain an induction error."""

        ordered: list[ExactEditionBinding] = []
        seen: set[ExactEditionBinding] = set()
        for identifier in evidence_kind_identifiers:
            owner = self.owner_for(evidence_kind_identifier=identifier)
            if owner is None or owner in seen:
                continue
            seen.add(owner)
            ordered.append(owner)
        return tuple(ordered)


def reference_profile_evidence_kind_ownership_registry() -> (
    EvidenceKindOwnershipRegistry
):
    return EvidenceKindOwnershipRegistry(
        bindings=_built_in_evidence_kind_owner_bindings()
    )


def _built_in_evidence_kind_owner_bindings() -> tuple[EvidenceKindOwnerBinding, ...]:
    profile_owner = resolve_reference_profile_edition_binding(selection_token="0.5")
    agent_owner = resolve_reference_profile_companion_binding(
        companion_identifier=str(AGENT_ADMISSION_COMPANION_IDENTIFIER)
    )
    python_owner = resolve_reference_profile_companion_binding(
        companion_identifier=str(PYTHON_COMPANION_IDENTIFIER)
    )
    return (
        *(
            EvidenceKindOwnerBinding(
                evidence_kind_identifier=str(identifier),
                owner=profile_owner,
            )
            for identifier in REFERENCE_PROFILE_EVIDENCE_KINDS
        ),
        *(
            EvidenceKindOwnerBinding(
                evidence_kind_identifier=str(identifier),
                owner=agent_owner,
            )
            for identifier in AGENT_ADMISSION_EVIDENCE_KINDS
        ),
        *(
            EvidenceKindOwnerBinding(
                evidence_kind_identifier=str(identifier),
                owner=python_owner,
            )
            for identifier in PYTHON_EVIDENCE_KINDS
        ),
    )
