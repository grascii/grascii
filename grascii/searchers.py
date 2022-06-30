"""
Contains the base class for Searchers as well as multiple concrete
implementations of it.
"""

from __future__ import annotations

import re
import sys
from abc import ABC, abstractmethod
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    List,
    Match,
    NamedTuple,
    Optional,
    Pattern,
    Sequence,
    Set,
    Tuple,
    TypeVar,
)

from lark.exceptions import UnexpectedInput

from grascii import defaults, grammar, metrics, regen
from grascii.dictionary import get_dict_file
from grascii.metrics import Comparable
from grascii.parser import GrasciiParser, Interpretation

IT = TypeVar("IT")
CT = TypeVar("CT", bound=Comparable)


class DictionaryEntry(NamedTuple):

    grascii: str
    translation: str


class SearchResult(Generic[IT]):
    def __init__(
        self,
        matches: List[Tuple[IT, Match[str]]],
        entry: DictionaryEntry,
        dictionary: str,
    ) -> None:
        self.matches = matches
        self.entry = entry
        self.dictionary = dictionary


class Searcher(ABC, Generic[IT]):

    """An abstract base class for objects that search Grascii dictionaries."""

    def __init__(self, **kwargs: Any) -> None:
        self.dictionaries: List[str] = (
            kwargs.get("dictionaries")
            if kwargs.get("dictionaries")
            else defaults.SEARCH["Dictionary"].split()
        )

    def perform_search(
        self,
        patterns: Iterable[Tuple[IT, Pattern[str]]],
        starting_letters: Set[str],
    ) -> Iterable[SearchResult[IT]]:
        """Performs a search of a Grascii Dictionary.

        :param patterns: A collection of compiled regular expression patterns
            with a corresponding interpretation.
        :param starting_letters: A set of letters used to index the search in
            a Grascii Dictionary.
        :param metric: A function taking an interpretation and a regular
            expression match that returns a positive integer signifying the
            difference between the interpretation and the match. 0 means the
            two are equivalent. The greater the value, the more different
            they are.
        :returns: A collection strings of the form "[grascii] [translation]"
            sorted by the results of metric.
        """
        for dict_name in self.dictionaries:
            for item in sorted(starting_letters):
                try:
                    dict_file = get_dict_file(dict_name, item)
                except FileNotFoundError:
                    continue
                with dict_file as dictionary:
                    for line in dictionary:
                        matches = []
                        for interp, pattern in patterns:
                            match = pattern.search(line)
                            if match:
                                matches.append((interp, match))
                        if matches:
                            grascii, translation = line.strip().split(maxsplit=1)
                            entry = DictionaryEntry(grascii, translation)
                            yield SearchResult(matches, entry, dict_name)

    @abstractmethod
    def search(self, **kwargs: Any) -> Optional[Iterable[SearchResult[IT]]]:
        """An abstract method that runs a search with the given search
        options and returns the results."""
        ...

    def sorted_search(
        self,
        metric: Callable[[SearchResult[IT]], CT] = metrics.get_trivial(),
        **kwargs: Any,
    ) -> Sequence[SearchResult[IT]]:

        results = []
        for result in self.search(**kwargs):
            results.append((result, metric(result)))
            i = len(results) - 1
            while i > 0:
                if results[i][1] < results[i - 1][1]:
                    results[i - 1], results[i] = results[i], results[i - 1]
                i -= 1
        return [result for result, _ in results]


class GrasciiSearcher(Searcher[Interpretation]):

    """A subclass of Searcher that performs a search given a Grascii string"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._parser = GrasciiParser()

    def extract_search_args(self, **kwargs: Any) -> None:
        """Get the relevant arguments for search."""

        self.uncertainty = kwargs.get(
            "uncertainty", defaults.SEARCH.getint("Uncertainty")
        )
        # handle enum conversion error?
        try:
            self.search_mode = regen.SearchMode(
                kwargs.get("search_mode", defaults.SEARCH["SearchMode"])
            )
        except ValueError:
            self.search_mode = regen.SearchMode(
                defaults.DEFAULTS["Search"]["SearchMode"]
            )
        try:
            self.annotation_mode = regen.Strictness(
                kwargs.get("annotation_mode", defaults.SEARCH["AnnotationMode"])
            )
        except ValueError:
            self.annotation_mode = regen.Strictness(
                defaults.DEFAULTS["Search"]["AnnotationMode"]
            )
        try:
            self.aspirate_mode = regen.Strictness(
                kwargs.get("aspirate_mode", defaults.SEARCH["AspirateMode"])
            )
        except ValueError:
            self.aspirate_mode = regen.Strictness(
                defaults.DEFAULTS["Search"]["AspirateMode"]
            )
        try:
            self.disjoiner_mode = regen.Strictness(
                kwargs.get("disjoiner_mode", defaults.SEARCH["DisjoinerMode"])
            )
        except ValueError:
            self.disjoiner_mode = regen.Strictness(
                defaults.DEFAULTS["Search"]["DisjoinerMode"]
            )
        self.fix_first = kwargs.get("fix_first", False)
        self.interpretation_mode = kwargs.get(
            "interpretation", defaults.SEARCH["Interpretation"]
        )

    def search(self, **kwargs: Any) -> Optional[Iterable[SearchResult[Interpretation]]]:
        """
        :param grascii: [Required] The grascii string to use in the search.
        :param uncertainty: The uncertainty of the grascii string.
        :param search_mode: The search mode to use.
        :param annotation_mode: How to handle annotations in the search.
        :param aspirate_mode: How to handle annotations in the search.
        :param disjoiner_mode: How to handle annotations in the search.
        :param fix_first: Apply an uncertainty of 0 to the first token.
        :param interpretation: How to handle ambiguous grascii strings.
        :type grascii: str
        :type uncertainty: int: 0, 1, or 2
        :type search_mode: str: one of regen.SearchMode values
        :type annotation_mode: str: one of regen.Strictness values
        :type aspirate_mode: str: one of regen.Strictness values
        :type disjoiner_mode: str: one of regen.Strictness values
        :type fix_first: bool
        :type interpretation: "best" or "all"
        :returns: A list of search results.
        :rtype: List[str]
        """

        grascii = kwargs["grascii"].upper()
        self.extract_search_args(**kwargs)

        try:
            interpretations = self._parser.interpret(grascii)
        except UnexpectedInput as e:
            print("Invalid Grascii String", file=sys.stderr)
            print(e.get_context(grascii), file=sys.stderr)
            return None

        builder = regen.RegexBuilder(
            uncertainty=self.uncertainty,
            search_mode=self.search_mode,
            aspirate_mode=self.aspirate_mode,
            annotation_mode=self.annotation_mode,
            disjoiner_mode=self.disjoiner_mode,
            fix_first=self.fix_first,
        )

        interps = (
            interpretations[0:1]
            if self.interpretation_mode == "best"
            else interpretations
        )
        patterns = builder.generate_patterns_map(interps)
        starting_letters = builder.get_starting_letters(interps)

        return self.perform_search(patterns, starting_letters)

    def sorted_search(
        self,
        metric: Callable[[SearchResult[Interpretation]], CT] = metrics.standard,
        **kwargs: Any,
    ) -> Sequence[SearchResult[Interpretation]]:
        return super().sorted_search(metric, **kwargs)


class RegexSearcher(Searcher[str]):

    """A subclass of Searcher that searches a grascii dictionary given
    a raw regular expression."""

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)

    def search(self, **kwargs: Any) -> Iterable[SearchResult[str]]:
        """
        :param regexp: [Required] A regular expression to use in a search.
        :returns: A list of search results.
        :rtype: List[str]
        """

        regex = kwargs["regexp"]
        pattern = re.compile(regex)
        patterns = [(pattern.pattern, pattern)]

        starting_letters = grammar.HARD_CHARACTERS
        return self.perform_search(patterns, starting_letters)


class ReverseSearcher(RegexSearcher):

    """A subclass of RegexSearcher that searches a grascii dictionary
    given a word."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def search(self, **kwargs: Any) -> Iterable[SearchResult[str]]:
        """
        :param reverse: [Required] A word to search for.
        :returns: A list of search results.
        :rtype: List[str]
        """

        word = kwargs["reverse"]
        kwargs["regexp"] = (
            r"(?i)(?P<grascii>.+?\s+)"
            + f"(?P<translation>(.*\\s)?(?P<word>{word}).*)(\\s|\\Z)"
        )

        return super().search(**kwargs)

    def sorted_search(
        self,
        metric: Callable[[SearchResult[str]], CT] = metrics.translation_standard,
        **kwargs: Any,
    ) -> Sequence[SearchResult[str]]:
        return super().sorted_search(metric, **kwargs)
