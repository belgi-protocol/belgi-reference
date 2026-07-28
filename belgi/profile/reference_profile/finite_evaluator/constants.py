"""Closed identifiers for the exact Part 4 finite evaluator."""

from __future__ import annotations

from belgi.core import SemanticsKey as _SemanticsKey
from belgi.profile.edition_catalog import (
    exact_edition_document_for_key as _exact_edition_document_for_key,
)
from belgi.profile.reference_profile.declarations.source import (
    ALL_GENERIC_EVIDENCE_SOURCE_CLASSES as _ALL_GENERIC_EVIDENCE_SOURCE_CLASSES,
)
from belgi.profile.reference_profile.identifiers.binding_kinds import (
    ALL_BINDING_KINDS as _ALL_BINDING_KINDS,
)
from belgi.profile.reference_profile.identifiers.conditions import (
    CHANGE_BASIS_RESOLVED as _CHANGE_BASIS_RESOLVED,
)
from belgi.profile.reference_profile.identifiers.conditions import (
    REQUIRED_EVIDENCE_PRESENT as _REQUIRED_EVIDENCE_PRESENT,
)
from belgi.profile.reference_profile.identifiers.conditions import (
    REVIEW_POLICY_SATISFIED as _REVIEW_POLICY_SATISFIED,
)
from belgi.profile.reference_profile.identifiers.evidence_kinds import (
    ALL_EVIDENCE_KINDS as _ALL_EVIDENCE_KINDS,
)

__all__ = [
    "CHANGE_BASIS_SEMANTICS",
    "FINITE_CONDITIONS",
    "PART4_DESIGNATOR",
    "PART4_SHA256",
    "PART4_URI",
    "RECOGNIZED_BINDING_KINDS",
    "RECOGNIZED_EVIDENCE_KINDS",
    "RECOGNIZED_SOURCE_CLASSES",
    "REQUIRED_EVIDENCE_SEMANTICS",
    "REVIEW_POLICY_SEMANTICS",
]


_PART4_DOCUMENT = _exact_edition_document_for_key(
    key="software-change-admission-profile"
)
PART4_URI = _PART4_DOCUMENT.uri
PART4_SHA256 = _PART4_DOCUMENT.sha256
PART4_DESIGNATOR = _PART4_DOCUMENT.immutable_designator

FINITE_CONDITIONS = frozenset(
    {
        _CHANGE_BASIS_RESOLVED,
        _REQUIRED_EVIDENCE_PRESENT,
        _REVIEW_POLICY_SATISFIED,
    }
)

RECOGNIZED_EVIDENCE_KINDS = frozenset(str(kind) for kind in _ALL_EVIDENCE_KINDS)

RECOGNIZED_SOURCE_CLASSES = frozenset(
    str(source_class) for source_class in _ALL_GENERIC_EVIDENCE_SOURCE_CLASSES
)

RECOGNIZED_BINDING_KINDS = frozenset(str(kind) for kind in _ALL_BINDING_KINDS)

CHANGE_BASIS_SEMANTICS = _SemanticsKey(
    "belgi.software-change.finite-review-record.change-basis-resolved"
)
REQUIRED_EVIDENCE_SEMANTICS = _SemanticsKey(
    "belgi.software-change.finite-review-record.required-evidence-present"
)
REVIEW_POLICY_SEMANTICS = _SemanticsKey(
    "belgi.software-change.finite-review-record.review-policy-satisfied"
)
