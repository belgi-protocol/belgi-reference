"""Independent stable-identifier and exact-source rule selection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from belgi.carrier import ImmutableDesignator

__all__ = [
    "CANONICALIZATION_RULE_ROLE",
    "DIGEST_ALGORITHM_RULE_ROLE",
    "PROJECTION_RULE_ROLE",
    "RuleSourceBindingObservation",
    "RuleSourceValidation",
    "validate_rule_source_binding",
    "validate_selected_digest_rule",
]

DIGEST_ALGORITHM_RULE_ROLE = "digest-algorithm"
CANONICALIZATION_RULE_ROLE = "canonicalization-rule"
PROJECTION_RULE_ROLE = "projection-rule"
_RULE_ROLES = frozenset(
    {
        DIGEST_ALGORITHM_RULE_ROLE,
        CANONICALIZATION_RULE_ROLE,
        PROJECTION_RULE_ROLE,
    }
)


class _DigestRuleSupport(Protocol):
    def supports_digest_algorithm_identifier(self, *, identifier: str) -> bool: ...

    def supports_digest_algorithm_designator(
        self, *, designator: ImmutableDesignator
    ) -> bool: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleSourceBindingObservation:
    rule_role: str
    stable_identifier: str
    exact_source_designator: ImmutableDesignator
    source_assigned_identifier: str
    source_available: bool
    source_digest_verified: bool
    source_meaning_matches_selection: bool
    verifier_supported: bool
    fallback_attempted: bool

    def __post_init__(self) -> None:
        if self.rule_role not in _RULE_ROLES:
            raise ValueError(f"Unsupported rule-source role: {self.rule_role!r}.")


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleSourceValidation:
    accepted: bool
    reason: str | None


def validate_rule_source_binding(
    *, observation: RuleSourceBindingObservation
) -> RuleSourceValidation:
    checks = (
        (
            observation.stable_identifier == observation.source_assigned_identifier,
            "identifier-source-disagreement",
        ),
        (observation.source_available, "source-unavailable"),
        (observation.source_digest_verified, "source-digest-mismatch"),
        (
            observation.source_meaning_matches_selection,
            "source-meaning-mismatch",
        ),
        (observation.verifier_supported, "rule-unsupported"),
        (not observation.fallback_attempted, "fallback-prohibited"),
    )
    for satisfied, reason in checks:
        if not satisfied:
            return RuleSourceValidation(accepted=False, reason=reason)
    return RuleSourceValidation(accepted=True, reason=None)


def validate_selected_digest_rule(
    *,
    identifier: str,
    designator: ImmutableDesignator,
    support: _DigestRuleSupport,
) -> RuleSourceValidation:
    identifier_supported = support.supports_digest_algorithm_identifier(
        identifier=identifier
    )
    source_supported = support.supports_digest_algorithm_designator(
        designator=designator
    )
    return validate_rule_source_binding(
        observation=RuleSourceBindingObservation(
            rule_role=DIGEST_ALGORITHM_RULE_ROLE,
            stable_identifier=identifier,
            exact_source_designator=designator,
            source_assigned_identifier=identifier if identifier_supported else "",
            source_available=source_supported,
            source_digest_verified=source_supported,
            source_meaning_matches_selection=(
                identifier_supported and source_supported
            ),
            verifier_supported=identifier_supported and source_supported,
            fallback_attempted=False,
        )
    )
