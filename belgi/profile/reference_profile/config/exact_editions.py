from __future__ import annotations

from belgi.profile.companions.agent_admission.edition import (
    COMPANION_IDENTIFIER as AGENT_ADMISSION_IDENTIFIER,
)
from belgi.profile.companions.agent_admission.edition import (
    build_agent_admission_companion_edition,
)
from belgi.profile.companions.ci_trust.edition import (
    COMPANION_IDENTIFIER as CI_TRUST_IDENTIFIER,
)
from belgi.profile.companions.ci_trust.edition import (
    build_ci_trust_companion_edition,
)
from belgi.profile.companions.json_representation.edition import (
    COMPANION_IDENTIFIER as JSON_REPRESENTATION_IDENTIFIER,
)
from belgi.profile.companions.json_representation.edition import (
    build_json_representation_companion_edition,
)
from belgi.profile.companions.package_integrity_anchor.edition import (
    COMPANION_IDENTIFIER as PACKAGE_INTEGRITY_ANCHOR_IDENTIFIER,
)
from belgi.profile.companions.package_integrity_anchor.edition import (
    build_package_integrity_anchor_companion_edition,
)
from belgi.profile.companions.python.edition import (
    COMPANION_IDENTIFIER as PYTHON_IDENTIFIER,
)
from belgi.profile.companions.python.edition import (
    build_python_companion_edition,
)
from belgi.profile.edition import (
    ExactEdition,
    ExactEditionBinding,
)
from belgi.profile.edition_catalog import exact_edition_document_for_key
from belgi.profile.reference_profile.edition_info import (
    build_reference_profile_edition,
)
from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileAdmissionCompileError,
)

__all__ = [
    "mandatory_reference_profile_companion_binding",
    "resolve_reference_profile_companion_binding",
    "resolve_reference_profile_dependency_binding",
    "resolve_reference_profile_edition_binding",
    "supported_reference_profile_edition_bindings",
]


_REFERENCE_PROFILE_SELECTION_TOKEN = "0.5"


_REFERENCE_PROFILE_EDITIONS_BY_SELECTION_TOKEN: dict[str, ExactEdition] = {
    _REFERENCE_PROFILE_SELECTION_TOKEN: build_reference_profile_edition(
        immutable_designator=exact_edition_document_for_key(
            key="software-change-admission-profile"
        ).immutable_designator
    ),
}

_REFERENCE_PROFILE_COMPANIONS_BY_IDENTIFIER: dict[str, ExactEdition] = {
    str(AGENT_ADMISSION_IDENTIFIER): build_agent_admission_companion_edition(
        immutable_designator=exact_edition_document_for_key(
            key="agent-admission-companion"
        ).immutable_designator
    ),
    str(PACKAGE_INTEGRITY_ANCHOR_IDENTIFIER): (
        build_package_integrity_anchor_companion_edition(
            immutable_designator=exact_edition_document_for_key(
                key="package-integrity-anchor-companion"
            ).immutable_designator
        )
    ),
    str(CI_TRUST_IDENTIFIER): build_ci_trust_companion_edition(
        immutable_designator=exact_edition_document_for_key(
            key="ci-trust-boundary-companion"
        ).immutable_designator
    ),
    str(JSON_REPRESENTATION_IDENTIFIER): (
        build_json_representation_companion_edition(
            immutable_designator=exact_edition_document_for_key(
                key="json-representation-companion"
            ).immutable_designator
        )
    ),
    str(PYTHON_IDENTIFIER): build_python_companion_edition(
        immutable_designator=exact_edition_document_for_key(
            key="python-condition-vocabulary-companion"
        ).immutable_designator
    ),
}

_REFERENCE_PROFILE_DEPENDENCY_BINDINGS_BY_SELECTION_TOKEN: dict[
    str, ExactEditionBinding
] = {
    str(
        _REFERENCE_PROFILE_EDITIONS_BY_SELECTION_TOKEN[
            _REFERENCE_PROFILE_SELECTION_TOKEN
        ].binding.family_identifier
    ): _REFERENCE_PROFILE_EDITIONS_BY_SELECTION_TOKEN[
        _REFERENCE_PROFILE_SELECTION_TOKEN
    ].binding,
    **{
        identifier: edition.binding
        for identifier, edition in _REFERENCE_PROFILE_COMPANIONS_BY_IDENTIFIER.items()
    },
}


def resolve_reference_profile_edition_binding(
    *,
    selection_token: str,
) -> ExactEditionBinding:
    edition = _REFERENCE_PROFILE_EDITIONS_BY_SELECTION_TOKEN.get(selection_token)
    if edition is None:
        supported = ", ".join(sorted(_REFERENCE_PROFILE_EDITIONS_BY_SELECTION_TOKEN))
        raise ReferenceProfileAdmissionCompileError(
            semantic_slice="profile_exact_edition",
            detail=(
                "unsupported exact_edition token "
                f"{selection_token!r}; supported selection tokens: {supported}."
            ),
        )
    return edition.binding


def resolve_reference_profile_companion_binding(
    *,
    companion_identifier: str,
) -> ExactEditionBinding:
    edition = _REFERENCE_PROFILE_COMPANIONS_BY_IDENTIFIER.get(companion_identifier)
    if edition is None:
        supported = ", ".join(sorted(_REFERENCE_PROFILE_COMPANIONS_BY_IDENTIFIER))
        raise ReferenceProfileAdmissionCompileError(
            semantic_slice="selected_companions",
            detail=(
                "unsupported companion identifier "
                f"{companion_identifier!r}; supported identifiers: {supported}."
            ),
        )
    return edition.binding


def resolve_reference_profile_dependency_binding(
    *,
    selection_token: str,
) -> ExactEditionBinding:
    binding = _REFERENCE_PROFILE_DEPENDENCY_BINDINGS_BY_SELECTION_TOKEN.get(
        selection_token
    )
    if binding is None:
        supported = ", ".join(
            sorted(_REFERENCE_PROFILE_DEPENDENCY_BINDINGS_BY_SELECTION_TOKEN)
        )
        raise ReferenceProfileAdmissionCompileError(
            semantic_slice="replay_relevant_dependencies",
            detail=(
                "unsupported exact_edition_dependencies selection token "
                f"{selection_token!r}; supported selection tokens: {supported}."
            ),
        )
    return binding


def mandatory_reference_profile_companion_binding() -> ExactEditionBinding:
    return _REFERENCE_PROFILE_COMPANIONS_BY_IDENTIFIER[
        str(PACKAGE_INTEGRITY_ANCHOR_IDENTIFIER)
    ].binding


def supported_reference_profile_edition_bindings() -> tuple[ExactEditionBinding, ...]:
    return tuple(
        edition.binding
        for _, edition in sorted(_REFERENCE_PROFILE_EDITIONS_BY_SELECTION_TOKEN.items())
    )
