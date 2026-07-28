from __future__ import annotations

from collections.abc import Mapping

from belgi.carrier.claim_record.model import (
    DependencyDeclaration,
    DependencyKind,
)
from belgi.carrier.exceptions import ClaimRecordError
from belgi.carrier.inventory import CanonicalReference
from belgi.carrier.parse_support import (
    require_allowed_keys,
    require_mapping_object,
    require_non_empty_text,
)

__all__ = ["parse_dependency_declarations"]


def parse_dependency_declarations(
    *, value: object
) -> tuple[DependencyDeclaration, ...]:
    payload = require_mapping_object(
        value=value,
        label="claim record.dependencyDeclarations",
        error_type=ClaimRecordError,
    )
    declarations: list[DependencyDeclaration] = []
    for dependent_reference_text, targets_payload in payload.items():
        if not isinstance(dependent_reference_text, str):
            raise ClaimRecordError(
                "dependencyDeclarations keys must be canonical references."
            )
        targets = require_mapping_object(
            value=targets_payload,
            label=f"claim record.dependencyDeclarations.{dependent_reference_text}",
            error_type=ClaimRecordError,
        )
        declarations.extend(
            _parse_dependency_targets(
                dependent_reference_text=dependent_reference_text,
                targets=targets,
            )
        )
    return tuple(declarations)


def _parse_dependency_targets(
    *,
    dependent_reference_text: str,
    targets: Mapping[str, object],
) -> tuple[DependencyDeclaration, ...]:
    declarations: list[DependencyDeclaration] = []
    for dependency_reference_text, target_payload in targets.items():
        if not isinstance(dependency_reference_text, str):
            raise ClaimRecordError(
                "dependency target keys must be canonical references."
            )
        label = (
            "claim record.dependencyDeclarations."
            f"{dependent_reference_text}.{dependency_reference_text}"
        )
        target = require_mapping_object(
            value=target_payload,
            label=label,
            error_type=ClaimRecordError,
        )
        require_allowed_keys(
            payload=target,
            label=label,
            allowed_keys=frozenset({"dependencyKinds"}),
            error_type=ClaimRecordError,
        )
        kinds = target.get("dependencyKinds")
        if not isinstance(kinds, list) or not kinds:
            raise ClaimRecordError("dependencyKinds must be a non-empty array.")
        declarations.extend(
            DependencyDeclaration(
                dependent_reference=CanonicalReference(dependent_reference_text),
                dependency_reference=CanonicalReference(dependency_reference_text),
                dependency_kind=DependencyKind(
                    require_non_empty_text(
                        value=kind,
                        label=f"{label}.dependencyKinds[]",
                        error_type=ClaimRecordError,
                    )
                ),
            )
            for kind in kinds
        )
    return tuple(declarations)
