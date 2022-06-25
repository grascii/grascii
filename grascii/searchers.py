"""
Contains the base class for Searchers as well as multiple concrete
implementations of it.
"""

import re
import sys
from abc import ABC, abstractmethod
from typing import Callable, Iterable, List, Match, Pattern, Set, Tuple, TypeVar

from lark import UnexpectedInput

from grascii import defaults, grammar, metrics, regen
from grascii.dictionary import get_dict_file
from grascii.parser import GrasciiParser

T = TypeVar("T")


class Searcher(ABC):

    """An abstract base class for objects that search Grascii dictionaries."""

    def __init__(self, **kwargs):
        self.dictionaries = (
            kwargs.get("dictionaries")
            if kwargs.get("dictionaries")
            else defaults.SEARCH["Dictionary"].split()
        )

    def perform_search(
        self,
        patterns: Iterable[Tuple[T, Pattern]],
        starting_letters: Set[str],
        metric: Callable[[T, Match], int],
    ) -> Iterable[str]:
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
        sorted_results: List[Tuple[str, int]] = []
        for dict_name in self.dictionaries:
            for item in sorted(starting_letters):
                try:
                    with get_dict_file(dict_name, item) as dictionary:
                        for line in dictionary:
                            found_match = False
                            diff = None
                            for interp, pattern in patterns:
                                match = pattern.search(line)
                                if match:
                                    found_match = True
                                    distance = metric(interp, match)
                                    if diff is None or distance < diff:
                                        diff = distance
                            if found_match:
                                i = len(sorted_results)
                                sorted_results.append((line, diff))
                                while i > 0:
                                    if sorted_results[i][1] < sorted_results[i - 1][1]:
                                        tmp = sorted_results[i - 1]
                                        sorted_results[i - 1] = sorted_results[i]
                                        sorted_results[i] = tmp
                                    i -= 1
                except FileNotFoundError:
                    pass
                    # print("Error: Could not find", dict_path + item)
        for tup in sorted_results:
            yield tup[0].strip()

    @abstractmethod
    def search(self, **kwargs):
        """An abstract method that runs a search with the given search
        options and returns the results."""
        ...


class GrasciiSearcher(Searcher):

    """A subclass of Searcher that performs a search given a Grascii string"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._parser = GrasciiParser()

    def extract_search_args(self, **kwargs):
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

    def search(self, **kwargs):
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
            return

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

        results = self.perform_search(patterns, starting_letters, metrics.standard)
        return list(results)


class RegexSearcher(Searcher):

    """A subclass of Searcher that searches a grascii dictionary given
    a raw regular expression."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def search(self, **kwargs):
        """
        :param regexp: [Required] A regular expression to use in a search.
        :returns: A list of search results.
        :rtype: List[str]
        """

        regex = kwargs["regexp"]
        pattern = re.compile(regex)
        patterns = [(pattern.pattern, pattern)]

        if "metric" in kwargs:
            metric = kwargs["metric"]
        else:

            def metric(s: str, m: Match):
                return 0

        starting_letters = grammar.HARD_CHARACTERS
        results = self.perform_search(patterns, starting_letters, metric)
        return list(results)


class ReverseSearcher(RegexSearcher):

    """A subclass of RegexSearcher that searches a grascii dictionary
    given a word."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def search(self, **kwargs):
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

        def metric(s: str, match: Match):
            word_start = match.start("word") - match.end("grascii")
            return word_start, len(match.group("translation"))

        kwargs["metric"] = metric
        return super().search(**kwargs)
