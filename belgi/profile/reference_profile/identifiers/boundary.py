from __future__ import annotations

from belgi.profile.governance import BoundaryParticipationId

__all__ = [
    "ALL_BOUNDARY_PARTICIPATIONS",
    "EXCLUDED",
    "INCLUDED",
]


INCLUDED = BoundaryParticipationId(
    "belgi.software-change.boundary-participation.included"
)
EXCLUDED = BoundaryParticipationId(
    "belgi.software-change.boundary-participation.excluded"
)

ALL_BOUNDARY_PARTICIPATIONS: tuple[BoundaryParticipationId, ...] = (
    INCLUDED,
    EXCLUDED,
)
