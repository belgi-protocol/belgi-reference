"""Production observations for the JSON representation corpus."""

from __future__ import annotations

from .corpus import (
    JSON_REPRESENTATION_CORPUS_SHA256,
    JSON_REPRESENTATION_CORPUS_URI,
    execute_json_representation_corpus,
    run_builtin_json_representation_corpus,
)
from .model import JSONRepresentationCorpusReport

__all__ = [
    "JSON_REPRESENTATION_CORPUS_SHA256",
    "JSON_REPRESENTATION_CORPUS_URI",
    "JSONRepresentationCorpusReport",
    "execute_json_representation_corpus",
    "run_builtin_json_representation_corpus",
]
