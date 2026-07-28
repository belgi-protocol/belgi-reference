from __future__ import annotations

from belgi.profile.governance import ReplayPolicyId

__all__ = [
    "ALL_REPLAY_POLICIES",
    "RECORD_CHECK",
    "normalize_reference_profile_replay_policy_identifier",
]


RECORD_CHECK = ReplayPolicyId("belgi.software-change.replay.record-check")

ALL_REPLAY_POLICIES: tuple[ReplayPolicyId, ...] = (RECORD_CHECK,)


def normalize_reference_profile_replay_policy_identifier(
    *,
    value: str,
) -> ReplayPolicyId:
    if not value:
        raise ValueError("replay_policy_identifier must not be empty.")
    if value == str(RECORD_CHECK):
        return RECORD_CHECK
    raise ValueError(f"unsupported replay policy identifier: {value!r}.")
