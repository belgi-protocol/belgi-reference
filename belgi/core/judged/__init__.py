from __future__ import annotations

from typing import TypeAlias as _TypeAlias

from .admission_subject import AdmissionSubject
from .projection import JudgedObject, project_judged_object
from .reference_context import ReferenceContext

J: _TypeAlias = JudgedObject

__all__ = [
    "AdmissionSubject",
    "J",
    "JudgedObject",
    "ReferenceContext",
    "project_judged_object",
]
