from __future__ import annotations

from belgi.profile.edition import ProfileIdentifier

PROFILE_IDENTIFIER = ProfileIdentifier(
    "https://belgi.dev/ids/profile/software-change-admission"
)

__all__ = [
    "PROFILE_IDENTIFIER",
    "normalize_reference_profile_identifier",
]


def normalize_reference_profile_identifier(*, value: str) -> ProfileIdentifier:
    if not value:
        raise ValueError("profile_identifier must not be empty.")
    if value == str(PROFILE_IDENTIFIER):
        return PROFILE_IDENTIFIER
    raise ValueError(f"unsupported reference-profile identifier: {value!r}.")
