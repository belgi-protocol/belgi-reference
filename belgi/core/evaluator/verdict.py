from __future__ import annotations

from enum import IntEnum

__all__ = ["GO", "NO_GO", "Verdict"]


class Verdict(IntEnum):
    NO_GO = 0
    GO = 1

    @classmethod
    def from_bool(cls, *, value: bool) -> Verdict:
        return cls.GO if value else cls.NO_GO


GO = Verdict.GO
NO_GO = Verdict.NO_GO
