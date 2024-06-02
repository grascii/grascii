"""
Contains the base class for Searchers as well as multiple concrete
implementations of it.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
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

from grascii import defaults, grammar, metrics, regen
from grascii.dictionary import Dictionary
from grascii.parser import GrasciiParser, Interpretation

if TYPE_CHECKING:
    from grascii.metrics import Comparable

IT = TypeVar("IT")


class DictionaryEntry(NamedTuple):
    grascii: str
    translation: str


class SearchResult(Generic[IT]):
    def __init__(
        self,
        matches: List[Tuple[IT, Match[str]]],
        entry: DictionaryEntry,
        dictionary: Dictionary,
    ) -> None:
        self.matches = matches
        self.entry = entry
        self.dictionary = dictionary


class Searcher(ABC, Generic[IT]):

    """An abstract base class for objects that search Grascii dictionaries.

    :param dictionaries: The dictionaries to search.
    :type dictionaries: List[str]
    """

    def __init__(self, **kwargs: Any) -> None:
        dictionaries = (
            kwargs.get("dictionaries")
            if kwargs.get("dictionaries")
            else defaults.SEARCH["Dictionary"].split()
        )
        self.dictionaries = [Dictionary.new(name) for name in dictionaries]

    def perform_search(
        self,
        patterns: Iterable[Tuple[IT, Pattern[str]]],
        starting_letters: Set[str],
    ) -> Iterable[SearchResult[IT]]:
        """Perform a search of a Grascii Dictionary.

        :param patterns: An iterable of interpretations and corresponding compiled
            regular expression patterns.
        :param starting_letters: A set of letters used to index the search in
            a Grascii Dictionary.
        :returns: An iterable of search results
        """
        for dictionary in self.dictionaries:
            for item in sorted(starting_letters):
                try:
                    dict_file = dictionary.open(item)
                except FileNotFoundError:
                    continue
                with dict_file:
                    for line in dict_file:
                        matches = []
                        for interp, pattern in patterns:
                            match = pattern.search(line)
                            if match:
                                matches.append((interp, match))
                        if matches:
                            grascii, translation = line.strip().split(maxsplit=1)
                            entry = DictionaryEntry(grascii, translation)
                            yield SearchResult(matches, entry, dictionary)

    @abstractmethod
    def search(self, **kwargs: Any) -> Optional[Iterable[SearchResult[IT]]]:
        """An abstract method that runs a search with the given search
        options and returns the results."""
        ...

    def sorted_search(
        self,
        metric: Callable[[SearchResult[IT]], Comparable] = metrics.trivial,
        **kwargs: Any,
    ) -> Sequence[SearchResult[IT]]:
        """Run a search with the given args and sort the search results by the
        given metric.
        """

        search_results = self.search(**kwargs)
        if search_results:
            return sorted(search_results, key=lambda r: metric(r))
        return []


class GrasciiSearcher(Searcher[Interpretation]):

    """A subclass of Searcher that performs a search given a Grascii string.

    :param dictionaries: The dictionaries to search.
    :type dictionaries: List[str]
    """

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

        interpretations = self._parser.interpret(grascii)

        builder = regen.RegexBuilder(
            uncertainty=self.uncertainty,
            search_mode=self.search_mode,
            aspirate_mode=self.aspirate_mode,
            annotation_mode=self.annotation_mode,
            disjoiner_mode=self.disjoiner_mode,
            fix_first=self.fix_first,
        )

        interps = (
            [next(interpretations)]
            if self.interpretation_mode == "best"
            else list(interpretations)
        )
        patterns = builder.generate_patterns_map(interps)
        starting_letters = builder.get_starting_letters(interps)

        return self.perform_search(patterns, starting_letters)

    def sorted_search(
        self,
        metric: Callable[
            [SearchResult[Interpretation]], Comparable
        ] = metrics.grascii_standard,
        **kwargs: Any,
    ) -> Sequence[SearchResult[Interpretation]]:
        return super().sorted_search(metric, **kwargs)


class RegexSearcher(Searcher[str]):

    """A subclass of Searcher that searches a grascii dictionary given
    a raw regular expression.

    :param dictionaries: The dictionaries to search.
    :type dictionaries: List[str]
    """

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
    given a word.

    :param dictionaries: The dictionaries to search.
    :type dictionaries: List[str]
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def search(self, **kwargs: Any) -> Iterable[SearchResult[str]]:
        """
        :param reverse: [Required] A word to search for.
        :returns: A list of search results.
        :rtype: List[str]
        """

        word = kwargs["reverse"]
        escaped_word = re.escape(word)
        kwargs["regexp"] = (
            r"(?i)(?P<grascii>.+?\s+)"
            + f"(?P<translation>(.*\\s)?(?P<word>{escaped_word}).*)(\\s|\\Z)"
        )

        return super().search(**kwargs)

    def sorted_search(
        self,
        metric: Callable[
            [SearchResult[str]], Comparable
        ] = metrics.translation_standard,
        **kwargs: Any,
    ) -> Sequence[SearchResult[str]]:
        return super().sorted_search(metric, **kwargs)
