"""
Contains the base class for Searchers as well as multiple concrete 
implementations of it. 
"""

from abc import ABC, abstractmethod
from functools import reduce
import re
import sys
from typing import Union, List, Set, Iterable, Dict, TypeVar, Callable, Pattern, Tuple, Match

from lark import Lark, Tree, UnexpectedInput, Transformer, Token
from lark.visitors import CollapseAmbiguities

from grascii import regen, metrics, grammar, defaults
from grascii.dictionary import get_dict_file
from grascii.grammars import get_grammar
from grascii.types import Interpretation


class GrasciiFlattener(Transformer):

    """This is a Lark Transformer that converts a parsed Grascii string
    into an Interpretation. An Interpretation is a list of terminals and
    annotation lists. Each terminal is its own element in the interpretation,
    but sequences of annotation terminals are grouped into their own sublist.
    """

    def start(self, children) -> Interpretation:
        """Returns the final result of the transformation.
        
        :meta private:
        """

        result: Interpretation = list()
        for child in children:
            for token in child:
                if token in grammar.ANNOTATION_CHARACTERS:
                    # pack annotation terminals into sublist
                    if isinstance(result[-1], list):
                        # add to previous annotation list
                        result[-1].append(token)
                    else:
                        # start new annotation list
                        result.append([token])
                else:
                    result.append(token)
        return result

    def __default__(self, data, children, meta) -> List[str]:
        """The default visitor function for nodes in the parse tree.
        Returns a flat list of strings."""

        result: List[str] = list()
        for child in children:
            if isinstance(child, Token):
                result.append(child)
            else:
                # flatten iterable
                for token in child:
                    result.append(token)
        return result

T = TypeVar("T")

class Searcher(ABC):

    """An abstract base class for objects that search as Grascii dictionary."""

    def __init__(self, **kwargs):
        self.dictionary = kwargs.get("dictionary", defaults.SEARCH["Dictionary"])

    def perform_search(self, patterns: Iterable[Tuple[T, Pattern]], starting_letters: Set[str], metric: Callable[[T, Match], int]) -> Iterable[str]:
        """Performs a search of a Grascii Dictionary.
        
        :param patterns: A collection of compiled regular expression patterns
            with a corresponding interpretation.
        :param starting_letters: A set of letters used to index the search in
            a Grascii Dictionary.
        :param metric: A function taking an interpretation and a regular 
            expression match that returns a positive integer signifying the
            differnce between the interpretation and the match. 0 means the
            two are equivalent. The greater the value, the more different
            they are.
        :returns: A collection strings of the form "[grascii] [translation]"
            sorted by the results of metric.
        """
        sorted_results: List[Tuple[str, int]] = list()
        for item in sorted(starting_letters):
            try:
                with get_dict_file(self.dictionary, item) as dictionary:
                    for line in dictionary:
                        found_match = False
                        diff = 2^32 - 1
                        for interp, pattern in patterns:
                            match = pattern.search(line)
                            if match:
                                found_match = True
                                diff = min(diff, metric(interp, match))
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
            yield tup[0]

    @abstractmethod
    def search(self, **kwargs):
        """An abstract method that runs a search with the given search
        options and returns the results."""
        ...

class GrasciiSearcher(Searcher):

    """A subclass of Searcher that performs a search given a Grascii string"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        grammar = get_grammar("grascii")
        self.parser = Lark.open(grammar, parser="earley", ambiguity="explicit")

    def parse_grascii(self, grascii: str) -> Union[Tree, bool]:
        """Attempt to parse a grascii string.

        :param grascii: The grascii string to parse.
        :returns: A Lark parse tree on a successful parse, or False if the
            parse fails.
        """

        try:
            return self.parser.parse(grascii)
        except UnexpectedInput as e:
            print("Invalid Grascii String", file=sys.stderr)
            print(e.get_context(grascii), file=sys.stderr)
            return False

    def flatten_tree(self, parse_tree: Tree) -> List[Interpretation]:
        """Extract a list of all possible Interpretations from a grascii
            parse tree.

        :param parse_tree: A Lark parse tree from a parsed grascii string.
        :returns: A list of all possible Interpretations.
        """

        trees = CollapseAmbiguities().transform(parse_tree)
        trans = GrasciiFlattener()
        return [trans.transform(tree) for tree in trees]

    def interpretation_to_string(self, interpretation: Interpretation) -> str:
        """Generate a string representation of an Interpretation.
        
        :param interpretation: An Interpretation to generate a string for.
        :returns: A string representation of an Interpretation
        """

        def reducer(builder, token):
            if isinstance(token, list):
                builder += token
            else:
                if builder and builder[-1] != "^" and token != "^":
                    builder.append("-")
                builder.append(token)
            return builder

        return "".join(reduce(reducer, interpretation, []))

    def get_unique_interpretations(self, interpretations: List[Interpretation]) -> Dict[str, Interpretation]:
        """Generate a collection of all unique Interpretations in another
        collection by comparing string representations.
        
        :param interpretations: A collection of Interpretations to process
        :returns: A dictionary mapping interpretation string representations
            to Interpretations.
        """

        return {self.interpretation_to_string(interp): interp for interp in interpretations}

    def extract_search_args(self, **kwargs):
        """Get the relevant arguments for search."""

        self.uncertainty = kwargs.get("uncertainty", defaults.SEARCH.getint("Uncertainty"))
        # handle enum conversion error?
        try:
            self.search_mode = regen.SearchMode(kwargs.get("search_mode", defaults.SEARCH["SearchMode"]))
        except ValueError:
            self.search_mode = regen.SearchMode(defaults.DEFAULTS["Search"]["SearchMode"])
        try:
            self.annotation_mode = regen.Strictness(kwargs.get("annotation_mode", defaults.SEARCH["AnnotationMode"]))
        except ValueError:
            self.annotation_mode = regen.Strictness(defaults.DEFAULTS["Search"]["AnnotationMode"])
        try:
            self.aspirate_mode = regen.Strictness(kwargs.get("aspirate_mode", defaults.SEARCH["AspirateMode"]))
        except ValueError:
            self.aspirate_mode = regen.Strictness(defaults.DEFAULTS["Search"]["AspirateMode"])
        try:
            self.disjoiner_mode = regen.Strictness(kwargs.get("disjoiner_mode", defaults.SEARCH["DisjoinerMode"]))
        except:
            self.disjoiner_mode = regen.Strictness(defaults.DEFAULTS["Search"]["DisjoinerMode"])
        self.fix_first = kwargs.get("fix_first", False)
        self.interpretation_mode = kwargs.get("interpretation", defaults.SEARCH["Interpretation"])

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
        :type annotation_mode: one of regen.Strictness values
        :type aspirate_mode: one of regen.Strictness values
        :type disjoiner_mode: one of regen.Strictness values
        :type fix_first: bool
        :type interpretation: "best" or "all"
        :returns: A list of search results.
        :rtype: List[str]
        """

        grascii = kwargs["grascii"].upper()
        self.extract_search_args(**kwargs)
        tree = self.parse_grascii(grascii)
        if not tree:
            return

        interpretations = self.flatten_tree(tree)
        interpretations = list(self.get_unique_interpretations(interpretations).values())
        builder = regen.RegexBuilder(
            uncertainty=self.uncertainty,
            search_mode=self.search_mode,
            aspirate_mode=self.aspirate_mode,
            annotation_mode=self.annotation_mode,
            disjoiner_mode=self.disjoiner_mode,
            fix_first=self.fix_first
        )

        interps = interpretations[0:1] if self.interpretation_mode == "best" else interpretations
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
        print(regex)
        pattern = re.compile(regex)
        patterns = [(pattern.pattern, pattern)]
        metric = lambda str, Match: 0
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
        kwargs["regexp"] = r".*\s" + word.capitalize()
        return super().search(**kwargs)
