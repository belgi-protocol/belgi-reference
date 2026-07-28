"""Closed mutation vocabulary for finite reference-validation inputs."""

from __future__ import annotations

import copy
from collections.abc import Mapping


def apply_case_mutations(
    *, base_input: Mapping[str, object], mutations: object
) -> dict[str, object]:
    """Apply only the corpus-declared add/remove/replace/append operations."""

    if not isinstance(mutations, list):
        raise ValueError("finite evaluator case mutations must be an array.")
    document = copy.deepcopy(dict(base_input))
    for index, mutation in enumerate(mutations):
        if not isinstance(mutation, Mapping):
            raise ValueError(f"finite evaluator mutation {index} must be an object.")
        operation = mutation.get("op")
        path = mutation.get("path")
        if operation not in {"add", "remove", "replace", "append"}:
            raise ValueError(f"finite evaluator mutation {index} op is unsupported.")
        if not isinstance(path, list) or not path:
            raise ValueError(f"finite evaluator mutation {index} path is invalid.")
        parent, key = _resolve_parent(document=document, path=path)
        if operation == "remove":
            _remove(parent=parent, key=key)
        elif operation == "append":
            target = _read(parent=parent, key=key)
            if not isinstance(target, list):
                raise ValueError(
                    f"finite evaluator mutation {index} append target is not an array."
                )
            target.append(copy.deepcopy(mutation.get("value")))
        else:
            _assign(
                parent=parent,
                key=key,
                value=copy.deepcopy(mutation.get("value")),
                require_existing=(operation == "replace"),
            )
    return document


def _resolve_parent(*, document: object, path: list[object]) -> tuple[object, object]:
    current = document
    for component in path[:-1]:
        current = _read(parent=current, key=component)
    return current, path[-1]


def _read(*, parent: object, key: object) -> object:
    if isinstance(parent, dict) and isinstance(key, str) and key in parent:
        return parent[key]
    if (
        isinstance(parent, list)
        and isinstance(key, int)
        and not isinstance(key, bool)
        and 0 <= key < len(parent)
    ):
        return parent[key]
    raise ValueError("finite evaluator mutation path does not resolve.")


def _remove(*, parent: object, key: object) -> None:
    if isinstance(parent, dict) and isinstance(key, str) and key in parent:
        del parent[key]
        return
    if (
        isinstance(parent, list)
        and isinstance(key, int)
        and not isinstance(key, bool)
        and 0 <= key < len(parent)
    ):
        parent.pop(key)
        return
    raise ValueError("finite evaluator remove path does not resolve.")


def _assign(
    *, parent: object, key: object, value: object, require_existing: bool
) -> None:
    if isinstance(parent, dict) and isinstance(key, str):
        if require_existing and key not in parent:
            raise ValueError("finite evaluator replace path does not resolve.")
        if not require_existing and key in parent:
            raise ValueError("finite evaluator add path already exists.")
        parent[key] = value
        return
    if (
        isinstance(parent, list)
        and isinstance(key, int)
        and not isinstance(key, bool)
        and 0 <= key < len(parent)
    ):
        if not require_existing:
            raise ValueError("finite evaluator add does not insert into arrays.")
        parent[key] = value
        return
    raise ValueError("finite evaluator assignment path does not resolve.")
