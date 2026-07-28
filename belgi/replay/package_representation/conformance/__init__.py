"""Production observations for replay-package representation conformance."""

from __future__ import annotations

from .corpus import (
    REPLAY_PACKAGE_REPRESENTATION_CORPUS_SHA256,
    REPLAY_PACKAGE_REPRESENTATION_CORPUS_URI,
    execute_replay_package_representation_corpus,
    run_builtin_replay_package_representation_corpus,
)
from .model import ReplayPackageRepresentationCorpusReport

__all__ = [
    "REPLAY_PACKAGE_REPRESENTATION_CORPUS_SHA256",
    "REPLAY_PACKAGE_REPRESENTATION_CORPUS_URI",
    "ReplayPackageRepresentationCorpusReport",
    "execute_replay_package_representation_corpus",
    "run_builtin_replay_package_representation_corpus",
]
