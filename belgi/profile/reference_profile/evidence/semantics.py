from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeVar, cast

from belgi.profile.exceptions import ProfileError
from belgi.profile.reference_profile.declarations import (
    EvidencePresenceDeclaration,
    RequiredEvidenceBinding,
)
from belgi.profile.reference_profile.identifiers.authority import (
    AUTHORITATIVE,
    NON_AUTHORITATIVE,
)
from belgi.profile.reference_profile.identifiers.binding_kinds import SATISFIES
from belgi.profile.reference_profile.identifiers.boundary import INCLUDED

from .semantic_support.registry import authoritative_subject_supported
from .subject_access import subject_field

if TYPE_CHECKING:
    from belgi.core import EvidenceState, JudgedObject


__all__ = [
    "adapt_profile_sat",
    "bound_evidence_items",
    "required_evidence_presence_failures",
    "required_evidence_present_sat",
    "satisfies_required_evidence_present",
    "unwrap_profile_declaration",
]


_DeclarationT = TypeVar("_DeclarationT")


@dataclass(frozen=True, slots=True)
class _EvidenceItemView:
    identifier: str | None
    kind: str | None
    source_class: str | None
    boundary_participation: str | None
    authority_level: str | None


def _iter_evidence_items(evidence_state: object) -> tuple[object, ...]:
    for attribute_name in ("evidence_items", "items"):
        value = subject_field(evidence_state, attribute_name)
        if value is None:
            continue
        if isinstance(value, tuple):
            return value
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            return tuple(value)
    for method_name in ("iter_evidence_items", "iter_items"):
        method = getattr(evidence_state, method_name, None)
        if method is None or not callable(method):
            continue
        value = method()
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            return tuple(value)
    return ()


def unwrap_profile_declaration(
    condition: object,
    declaration_type: type[_DeclarationT],
) -> _DeclarationT:
    """Resolve profile declaration material from the condition bridge object.

    The canonical bridge is ``ProfileCondition`` from
    ``reference_profile.declarations``. A caller may provide a different object
    only if it exposes equivalent declaration-bearing attributes.
    """

    if isinstance(condition, declaration_type):
        return condition
    for attribute_name in (
        "profile_declaration",
        "declaration",
        "parameters",
        "payload",
    ):
        value = subject_field(condition, attribute_name)
        if isinstance(value, declaration_type):
            return value
    raise TypeError(
        f"condition does not carry {declaration_type.__name__} declaration material."
    )


def _item_view(item: object) -> _EvidenceItemView:
    def _text(*names: str) -> str | None:
        value = subject_field(item, *names)
        return str(value) if value is not None else None

    return _EvidenceItemView(
        identifier=_text("identifier", "evidence_id", "item_id"),
        kind=_text("kind", "evidence_kind", "kind_id"),
        source_class=_text("source_class", "evidence_source_class"),
        boundary_participation=_text("boundary_participation", "boundary"),
        authority_level=_text("authority_level", "authority"),
    )


_AUTHORITY_ORDER = {
    str(NON_AUTHORITATIVE): 1,
    str(AUTHORITATIVE): 2,
}


def _authority_meets_floor(
    *, item_view: _EvidenceItemView, minimum_authority: str
) -> bool:
    if item_view.boundary_participation != str(INCLUDED):
        return False
    observed = item_view.authority_level
    if observed is None:
        return False
    return _AUTHORITY_ORDER.get(observed, -1) >= _AUTHORITY_ORDER.get(
        minimum_authority, -1
    )


def _binding_matches(
    *,
    item: object,
    binding: RequiredEvidenceBinding,
    allowed_source_classes: frozenset[str],
    condition: object | None,
) -> bool:
    if str(binding.binding_kind) != str(SATISFIES):
        return False
    item_view = _item_view(item)
    if item_view.kind != str(binding.evidence_kind):
        return False
    if binding.exact_evidence_identifiers:
        if item_view.identifier not in binding.exact_evidence_identifiers:
            return False
    if binding.allowed_source_classes:
        if item_view.source_class not in allowed_source_classes:
            return False
    if not _authority_meets_floor(
        item_view=item_view,
        minimum_authority=str(binding.minimum_authority),
    ):
        return False
    if str(binding.minimum_authority) == str(
        AUTHORITATIVE
    ) and not authoritative_subject_supported(
        item=item,
        source_class=item_view.source_class,
        condition=condition,
    ):
        return False
    return True


def bound_evidence_items(
    *,
    evidence_state: object,
    binding: RequiredEvidenceBinding,
    condition: object | None = None,
) -> tuple[object, ...]:
    allowed_source_classes = frozenset(
        str(source_class) for source_class in binding.allowed_source_classes
    )
    return tuple(
        item
        for item in _iter_evidence_items(evidence_state)
        if _binding_matches(
            item=item,
            binding=binding,
            allowed_source_classes=allowed_source_classes,
            condition=condition,
        )
    )


def _item_interpretable(item: object) -> bool:
    interpretable_fields = (
        "outcome",
        "numeric_value",
        "severity",
        "failure_count",
        "approval_count",
        "blocking_count",
        "environment_terms",
        "equivalence_basis",
    )
    return any(
        subject_field(item, field_name) is not None
        for field_name in interpretable_fields
    )


def _required_evidence_binding_label(*, binding: RequiredEvidenceBinding) -> str:
    allowed_source_classes = (
        "*"
        if not binding.allowed_source_classes
        else ",".join(
            sorted(str(source_class) for source_class in binding.allowed_source_classes)
        )
    )
    return (
        f"{binding.evidence_kind}"
        f"[sources={allowed_source_classes};"
        f"min_authority={binding.minimum_authority};"
        f"minimum_count={binding.minimum_count}]"
    )


def required_evidence_presence_failures(
    *,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
    condition: object,
) -> tuple[str, ...]:
    del judged_object
    declaration = unwrap_profile_declaration(condition, EvidencePresenceDeclaration)
    failures: list[str] = []
    for binding in declaration.required_bindings:
        items = bound_evidence_items(
            evidence_state=evidence_state,
            binding=binding,
            condition=declaration,
        )
        if len(items) < binding.minimum_count:
            failures.append(
                "missing required evidence binding "
                f"{_required_evidence_binding_label(binding=binding)}: "
                f"matched {len(items)} item(s)."
            )
            continue
        if declaration.require_interpretable_bindings:
            uninterpretable_count = sum(
                1 for item in items if not _item_interpretable(item)
            )
            if uninterpretable_count:
                failures.append(
                    "uninterpretable evidence binding "
                    f"{_required_evidence_binding_label(binding=binding)}: "
                    f"{uninterpretable_count} matched item(s) lack required subject fields."
                )
    return tuple(failures)


def satisfies_required_evidence_present(
    *,
    judged_object: JudgedObject,
    evidence_state: EvidenceState,
    condition: object,
) -> bool:
    return not required_evidence_presence_failures(
        judged_object=judged_object,
        evidence_state=evidence_state,
        condition=condition,
    )


def required_evidence_present_sat(
    judged_object: object,
    evidence_state: object,
    condition: object,
) -> bool:
    try:
        return satisfies_required_evidence_present(
            judged_object=cast("JudgedObject", judged_object),
            evidence_state=cast("EvidenceState", evidence_state),
            condition=condition,
        )
    except (AttributeError, ProfileError, ValueError):
        return False


def adapt_profile_sat(implementation):
    """Adapt a profile positional Sat function to the core keyword-only seam.

    This adapter does not swallow bridge errors. If the supplied ``condition``
    does not carry the profile declaration expected by the implementation,
    core's evaluator engine will surface that failure as ``SatExecutionError``.
    """

    def sat(*, judged: object, evidence: object, condition: object) -> bool:
        return implementation(judged, evidence, condition)

    cast(Any, sat).__belgi_provider_entrypoint__ = _profile_sat_provider_entrypoint(
        implementation
    )
    return sat


def _profile_sat_provider_entrypoint(implementation) -> str:
    module = getattr(implementation, "__module__", "")
    qualname = getattr(implementation, "__qualname__", "")
    if not module or not qualname:
        raise TypeError("profile Sat implementation must expose a stable entrypoint.")
    return f"{module}:{qualname}"
