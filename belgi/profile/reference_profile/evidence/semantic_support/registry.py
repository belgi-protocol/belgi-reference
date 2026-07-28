from __future__ import annotations

from collections.abc import Callable

from belgi.profile.reference_profile.companions.agent_admission.authority import (
    agent_admission_companion_authoritative_subject_supported,
)
from belgi.profile.reference_profile.declarations import (
    ARTIFACT_STORE_SOURCE,
    CI_EXECUTION_SOURCE,
    DEPENDENCY_ADVISORY_SERVICE_SOURCE,
    EXTERNAL_ANALYSIS_SERVICE_SOURCE,
    REPOSITORY_SYSTEM_SOURCE,
    REVIEW_SYSTEM_SOURCE,
)

from .artifact_store import artifact_store_authoritative_subject_supported
from .ci_execution import ci_execution_authoritative_subject_supported
from .dependency_advisory_service import (
    dependency_advisory_authoritative_subject_supported,
)
from .external_analysis_service import (
    external_analysis_authoritative_subject_supported,
)
from .repository_system import repository_system_authoritative_subject_supported
from .review_system import review_system_authoritative_subject_supported

__all__ = ["authoritative_subject_supported"]

_AuthoritativeSubjectSupporter = Callable[[object], bool]

_AUTHORITATIVE_SUBJECT_SUPPORTERS: dict[str, _AuthoritativeSubjectSupporter] = {
    str(ARTIFACT_STORE_SOURCE): artifact_store_authoritative_subject_supported,
    str(CI_EXECUTION_SOURCE): ci_execution_authoritative_subject_supported,
    str(REPOSITORY_SYSTEM_SOURCE): repository_system_authoritative_subject_supported,
    str(REVIEW_SYSTEM_SOURCE): review_system_authoritative_subject_supported,
    str(DEPENDENCY_ADVISORY_SERVICE_SOURCE): (
        dependency_advisory_authoritative_subject_supported
    ),
    str(EXTERNAL_ANALYSIS_SERVICE_SOURCE): (
        external_analysis_authoritative_subject_supported
    ),
}


def authoritative_subject_supported(
    *,
    item: object,
    source_class: str | None,
    condition: object | None = None,
) -> bool:
    if source_class is None:
        return False
    supporter = _AUTHORITATIVE_SUBJECT_SUPPORTERS.get(source_class)
    if supporter is None:
        return agent_admission_companion_authoritative_subject_supported(
            item=item,
            source_class=source_class,
        )
    if supporter is ci_execution_authoritative_subject_supported:
        return ci_execution_authoritative_subject_supported(
            item,
            condition=condition,
        )
    return supporter(item)
