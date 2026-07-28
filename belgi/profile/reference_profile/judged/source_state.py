from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, TypeGuard

from belgi.profile.reference_profile.exceptions import (
    ReferenceProfileSourceStateError,
)
from belgi.substrate.git.identity import require_commit_sha40, require_tree_sha40
from belgi.substrate.hash import sha256_bytes
from belgi.substrate.io import canonical_json_bytes

__all__ = [
    "ReferenceProfileJudgedSourceState",
    "has_reference_profile_judged_source_state_vocabulary",
    "reference_profile_proposal_identifier",
    "reference_profile_proposal_source_state_identifier",
    "require_reference_profile_judged_source_state",
]

_PROPOSAL_FIELDS = frozenset(
    {
        "identifier",
        "proposal_context_digests",
        "proposal_patch_digest",
        "source_state",
    }
)
_BASELINE_FIELDS = frozenset({"identifier", "source_state"})


class _GitObjectNormalizer(Protocol):
    def __call__(self, value: str, *, label: str) -> str: ...


@dataclass(frozen=True, slots=True, kw_only=True)
class ReferenceProfileJudgedSourceState:
    """Profile-owned source-state values that replay binds to preserved inputs."""

    patch_digest: str | None
    context_digests: tuple[str, ...]


def reference_profile_proposal_identifier(*, patch_digest: str | None) -> str:
    """Return the reference-profile identity for proposal patch material."""

    if patch_digest is None:
        return "proposal-observation"
    _require_sha256_digest(patch_digest, field="patch_digest")
    return f"urn:belgi:proposal-material:sha256:{patch_digest}"


def reference_profile_proposal_source_state_identifier(
    *,
    patch_digest: str | None,
    context_digests: tuple[str, ...],
) -> str | None:
    """Return the reference-profile identity for an ordered proposal snapshot."""

    if patch_digest is not None:
        _require_sha256_digest(patch_digest, field="patch_digest")
    if not isinstance(context_digests, tuple):
        raise ValueError("context_digests must be a tuple.")
    for ordinal, digest in enumerate(context_digests, start=1):
        _require_sha256_digest(digest, field=f"context_digests[{ordinal - 1}]")
    if patch_digest is None and not context_digests:
        return None
    payload = canonical_json_bytes(
        {
            "proposalPatchDigest": patch_digest,
            "proposalContextDigests": context_digests,
        }
    )
    return f"urn:belgi:proposal-source-state:sha256:{sha256_bytes(payload)}"


def has_reference_profile_judged_source_state_vocabulary(
    *, proposal: Mapping[str, object]
) -> bool:
    """Return whether a proposal declares the Part 4 source-state vocabulary."""

    return "proposal_patch_digest" in proposal or "proposal_context_digests" in proposal


def require_reference_profile_judged_source_state(
    *,
    proposal: Mapping[str, object],
    baseline: Mapping[str, object],
) -> ReferenceProfileJudgedSourceState:
    """Validate the closed Part 4 proposal and baseline source-state records."""

    if set(proposal) != _PROPOSAL_FIELDS or set(baseline) != _BASELINE_FIELDS:
        raise ReferenceProfileSourceStateError(
            detail="Part 4 judged source-state fields are incomplete."
        )
    raw_patch_digest = proposal.get("proposal_patch_digest")
    patch_digest = (
        None
        if raw_patch_digest is None
        else _require_profile_sha256(
            raw_patch_digest,
            field="proposal_patch_digest",
        )
    )
    context_digests = _require_context_digests(proposal.get("proposal_context_digests"))
    expected_proposal_identifier = reference_profile_proposal_identifier(
        patch_digest=patch_digest
    )
    if proposal.get("identifier") != expected_proposal_identifier:
        raise ReferenceProfileSourceStateError(
            detail="Part 4 proposal identifier does not bind the patch digest."
        )
    expected_source_state = reference_profile_proposal_source_state_identifier(
        patch_digest=patch_digest,
        context_digests=context_digests,
    )
    if proposal.get("source_state") != expected_source_state:
        raise ReferenceProfileSourceStateError(
            detail="Part 4 proposal source-state identifier is rebound."
        )
    _require_git_urn(
        baseline.get("identifier"),
        prefix="urn:belgi:git-commit:sha1:",
        label="baseline identifier",
        normalizer=require_commit_sha40,
    )
    _require_git_urn(
        baseline.get("source_state"),
        prefix="urn:belgi:git-tree:sha1:",
        label="baseline source state",
        normalizer=require_tree_sha40,
    )
    return ReferenceProfileJudgedSourceState(
        patch_digest=patch_digest,
        context_digests=context_digests,
    )


def _require_context_digests(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ReferenceProfileSourceStateError(
            detail="Part 4 proposal_context_digests must be a list."
        )
    return tuple(
        _require_profile_sha256(
            digest,
            field=f"proposal_context_digests[{index}]",
        )
        for index, digest in enumerate(value)
    )


def _require_profile_sha256(value: object, *, field: str) -> str:
    if not _is_lowercase_sha256_digest(value):
        raise ReferenceProfileSourceStateError(
            detail=f"{field} must be a lowercase SHA-256 digest."
        )
    return value


def _require_git_urn(
    value: object,
    *,
    prefix: str,
    label: str,
    normalizer: _GitObjectNormalizer,
) -> None:
    if not isinstance(value, str) or not value.startswith(prefix):
        raise ReferenceProfileSourceStateError(
            detail=f"Part 4 {label} is not a stable Git URN."
        )
    identity = value.removeprefix(prefix)
    try:
        normalized = normalizer(identity, label=label)
    except ValueError as exc:
        raise ReferenceProfileSourceStateError(
            detail=f"Part 4 {label} is not a stable Git URN."
        ) from exc
    if value != f"{prefix}{normalized}":
        raise ReferenceProfileSourceStateError(
            detail=f"Part 4 {label} is not canonical."
        )


def _require_sha256_digest(value: object, *, field: str) -> str:
    if not _is_lowercase_sha256_digest(value):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest.")
    return value


def _is_lowercase_sha256_digest(value: object) -> TypeGuard[str]:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )
