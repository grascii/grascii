# ruff: noqa: E402
from __future__ import annotations

APP_NAME = "grascii"
__version__ = "0.9.0"

from grascii.dictionary import Dictionary, DictionaryEntry, DictionaryType
from grascii.dictionary.build import (
    BuildMessage,
    BuildSummary,
    DictionaryBuilder,
    DictionaryOutputOptions,
)
from grascii.dictionary.pipeline import CancelPipeline, PipelineFunc
from grascii.interpreter import (
    GrasciiInterpreter,
    Interpretation,
    interpretation_to_string,
)
from grascii.parser import GrasciiParser, InvalidGrascii
from grascii.regen import SearchMode, Strictness
from grascii.searchers import (
    GrasciiSearcher,
    GrasciiSearchOptions,
    RegexSearcher,
    ReverseSearcher,
    Searcher,
    SearcherOptions,
    SearchResult,
)
from grascii.validator import GrasciiValidator

__all__ = [
    "Dictionary",
    "DictionaryEntry",
    "DictionaryType",
    "BuildMessage",
    "BuildSummary",
    "DictionaryBuilder",
    "DictionaryOutputOptions",
    "CancelPipeline",
    "PipelineFunc",
    "GrasciiInterpreter",
    "Interpretation",
    "interpretation_to_string",
    "GrasciiParser",
    "InvalidGrascii",
    "SearchMode",
    "Strictness",
    "GrasciiSearcher",
    "GrasciiSearchOptions",
    "RegexSearcher",
    "ReverseSearcher",
    "Searcher",
    "SearcherOptions",
    "SearchResult",
    "GrasciiValidator",
]
