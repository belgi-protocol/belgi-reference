from __future__ import annotations

from belgi.profile.governance import AuthorityLevelId

__all__ = [
    "ALL_AUTHORITY_LEVELS",
    "AUTHORITATIVE",
    "NON_AUTHORITATIVE",
]


AUTHORITATIVE = AuthorityLevelId("belgi.software-change.authority.authoritative")
NON_AUTHORITATIVE = AuthorityLevelId(
    "belgi.software-change.authority.non-authoritative"
)

ALL_AUTHORITY_LEVELS: tuple[AuthorityLevelId, ...] = (
    AUTHORITATIVE,
    NON_AUTHORITATIVE,
)
