from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass, field
from typing import NewType, TypeAlias, TypeVar

from belgi.core.validation import require_identifier

from .exceptions import (
    DuplicateIdentifierError,
    SemanticConstructionError,
)

ConditionId = NewType("ConditionId", str)
SemanticsKey = NewType("SemanticsKey", str)

__all__ = [
    "Condition",
    "ConditionId",
    "ConditionSemantics",
    "Evaluator",
    "ResolvedConditionSemantics",
    "SemanticsKey",
    "UndesignatedConditionSemantics",
    "UnrecoverableConditionSemantics",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class ResolvedConditionSemantics:
    semantics_key: SemanticsKey

    def __post_init__(self) -> None:
        require_identifier(
            owner="Evaluator", name="semantics_key", value=self.semantics_key
        )


@dataclass(frozen=True, slots=True)
class UndesignatedConditionSemantics:
    pass


@dataclass(frozen=True, slots=True)
class UnrecoverableConditionSemantics:
    pass


ConditionSemantics: TypeAlias = (
    ResolvedConditionSemantics
    | UndesignatedConditionSemantics
    | UnrecoverableConditionSemantics
)


@dataclass(frozen=True, slots=True, kw_only=True)
class Condition:
    condition_id: ConditionId
    determining_semantics: ConditionSemantics

    def __post_init__(self) -> None:
        require_identifier(
            owner="Evaluator", name="condition_id", value=self.condition_id
        )
        _require_condition_semantics(
            name="determining_semantics",
            value=self.determining_semantics,
        )

    @property
    def semantics_key(self) -> SemanticsKey | None:
        if isinstance(self.determining_semantics, ResolvedConditionSemantics):
            return self.determining_semantics.semantics_key
        return None

    @property
    def supports_evaluation(self) -> bool:
        return self.semantics_key is not None


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class Evaluator:
    """Extensional semantic evaluator object.

    Declaration collections are normalized lexicographically by identifier.
    Application order is not semantically meaningful for this evaluator.
    """

    declared_conditions: tuple[Condition, ...]
    _condition_index: dict[ConditionId, Condition] = field(
        init=False,
        repr=False,
        compare=False,
        hash=False,
    )

    def __eq__(self, other: object) -> bool:
        raise TypeError(
            "Evaluator equality is extensional and is not defined by declaration comparison."
        )

    def __post_init__(self) -> None:
        declared_conditions = tuple(self.declared_conditions)

        _ordered_unique_ids(
            values=declared_conditions,
            identifier=lambda condition: condition.condition_id,
            label="declared condition",
        )

        object.__setattr__(
            self,
            "declared_conditions",
            tuple(
                sorted(
                    declared_conditions,
                    key=lambda condition: str(condition.condition_id),
                )
            ),
        )
        object.__setattr__(
            self,
            "_condition_index",
            {
                condition.condition_id: condition
                for condition in self.declared_conditions
            },
        )

    @property
    def declared_condition_ids(self) -> frozenset[ConditionId]:
        return frozenset(
            condition.condition_id for condition in self.declared_conditions
        )

    def condition(self, *, condition_id: ConditionId) -> Condition | None:
        return self._condition_index.get(condition_id)


def _require_condition_semantics(*, name: str, value: ConditionSemantics) -> None:
    if not isinstance(
        value,
        (
            ResolvedConditionSemantics,
            UndesignatedConditionSemantics,
            UnrecoverableConditionSemantics,
        ),
    ):
        raise SemanticConstructionError(
            f"Evaluator {name} must be a ConditionSemantics instance."
        )


T = TypeVar("T")
IdentifierT = TypeVar("IdentifierT", bound=Hashable)


def _ordered_unique_ids(
    *,
    values: tuple[T, ...],
    identifier: Callable[[T], IdentifierT],
    label: str,
) -> tuple[IdentifierT, ...]:
    seen: set[IdentifierT] = set()
    ordered: list[IdentifierT] = []
    for value in values:
        value_id = identifier(value)
        if value_id in seen:
            raise DuplicateIdentifierError(f"Duplicate {label} identifier: {value_id}.")
        seen.add(value_id)
        ordered.append(value_id)
    return tuple(ordered)
