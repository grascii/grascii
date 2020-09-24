"""
Contains RegexBuilder for generating regular expression to use in grascii
searches.
"""

from enum import Enum
import re
from typing import List, Union, Iterable, Set, Pattern, Tuple

from grascii import grammar
from grascii.similarities import get_similar
from grascii.types import Interpretation

class SearchMode(Enum):
    """An enum representing different searh modes."""

    MATCH = "match"
    START = "start"
    CONTAIN = "contain"

class Strictness(Enum):
    """An enum representing different levels of strictness for handling
    annotations, aspirates, and disjoiners in grascii strings."""

    LOW = "discard"
    MEDIUM = "retain"
    HIGH = "strict"

class RegexBuilder():
    """A class used for generating regular expressions used to search from
    a grascii string based on grascii search options.
    
    :param uncertainty: The uncertainty of the grascii string.
    :param search_mode: The search mode to use.
    :param annotation_mode: How to handle annotations in the search.
    :param aspirate_mode: How to handle annotations in the search.
    :param disjoiner_mode: How to handle annotations in the search.
    :param fix_first: Apply an uncertainty of 0 to the first token.
    :type uncertainty: int: 0, 1, or 2
    :type search_mode: str: one of regen.SearchMode values
    :type annotation_mode: one of regen.Strictness values
    :type aspirate_mode: one of regen.Strictness values
    :type disjoiner_mode: one of regen.Strictness values
    :type fix_first: bool
    """

    def __init__(self, **kwargs):
        self.uncertainty = kwargs.get('uncertainty', 0)
        self.search_mode = kwargs.get('search_mode', SearchMode.MATCH)
        self.fix_first = kwargs.get('fix_first', False)
        self.annotation_mode = kwargs.get('annotation_mode', Strictness.LOW)
        self.aspirate_mode = kwargs.get('aspirate_mode', Strictness.LOW)
        self.disjoiner_mode = kwargs.get('disjoiner_mode', Strictness.HIGH)

    def make_annotation_regex(self, stroke: str, annotations: Iterable[str]) -> str:
        """Create a regular expression that matches the stroke with
        the acceptable annotations and given annotations according to
        the search options.
        
        :param stroke: The stroke for which to generate annotations.
        :param annotations: A collection of annotations used in generating
            the regular expression.

        :returns: A regular expression.
        """

        def pack(tup):
            if len(tup) == 1:
                return re.escape(tup[0]) + "?"
            return "[" + "".join(tup) + "]?"

        possible = grammar.ANNOTATIONS.get(stroke, list())

        if self.annotation_mode is Strictness.MEDIUM or \
                self.annotation_mode is Strictness.HIGH:
            builder = list()
            i = 0
            while i < len(possible):
                match = False
                for an in annotations:
                    if an in possible[i]:
                        builder.append(re.escape(an))
                        match = True
                        break
                if not match and self.annotation_mode is not Strictness.HIGH:
                    builder.append(pack(possible[i]))
                i += 1

            return stroke + "".join(builder)

        return stroke + "".join([pack(tup) for tup in possible])


    def make_uncertainty_regex(self, stroke: str, uncertainty: int, annotations: list=list()) -> str:
        """Create a regular expression that matches a stroke within a given
        uncertainty while applying provided annotations.
        
        :param stroke: The stroke for which to generate alternatives.
        :param uncertainty: The uncertainty to apply to the stroke.
        :param annotations: A list of annotations to use in the generation.
        :returns: A regular expression.
        """

        similars = get_similar(stroke, uncertainty)
        flattened = []
        for group in similars:
            for token in group:
                flattened.append(self.make_annotation_regex(token, annotations))

        return "(" + "|".join(flattened) + ")"

    def build_regex(self, interpretation: Interpretation) -> str:
        """Create a regular expression from a grascii interpretation based
        on the constructor search parameters.
        
        :param interpretation: The interpretation for which to generate a 
            regular expression.
        :returns: A regular expression.
        """

        aspirate = "(" + re.escape(grammar.ASPIRATE) + ")"
        disjoiner = "(" + re.escape(grammar.DISJOINER) + ")"

        builder = list()
        i = 0
        if self.search_mode is SearchMode.MATCH or \
                self.search_mode is SearchMode.START:
            builder.append("^")
            if self.aspirate_mode is Strictness.LOW:
                builder.append(aspirate)
                builder.append("?")
            if self.aspirate_mode is Strictness.MEDIUM:
                while i < len(interpretation) and interpretation[i] == grammar.ASPIRATE:
                    builder.append(aspirate)
                    i += 1
                if i < 2:
                    builder.append(aspirate)
                    builder.append("?")

        if self.search_mode is SearchMode.CONTAIN:
            builder.append(".*")

        found_first = False

        while i < len(interpretation):
            token = interpretation[i]

            if token == grammar.ASPIRATE:
                if self.aspirate_mode is Strictness.MEDIUM or \
                        self.aspirate_mode is Strictness.HIGH:
                    builder.append(aspirate)
                i += 1
                continue

            if token == grammar.DISJOINER:
                if self.disjoiner_mode is Strictness.MEDIUM or \
                        self.disjoiner_mode is Strictness.HIGH:
                    builder.append(disjoiner)
                i += 1
                continue

            uncertainty = self.uncertainty if found_first or not self.fix_first else 0
            insert_aspirate = False
            if token in grammar.STROKES:
                if builder[-1] != re.escape(grammar.ASPIRATE) and self.aspirate_mode is Strictness.MEDIUM and found_first:
                    insert_aspirate = True
                if self.disjoiner_mode is Strictness.LOW and found_first:
                    builder.append(disjoiner)
                    builder.append("?")
                if builder[-1] != re.escape(grammar.DISJOINER) and self.disjoiner_mode is Strictness.MEDIUM and found_first:
                    builder.append(disjoiner)
                    builder.append("?")
                if self.aspirate_mode is Strictness.LOW:
                    builder.append(aspirate)
                    builder.append("?")
                if insert_aspirate:
                    builder.append(aspirate)
                    builder.append("?")
                found_first = True

            if token in grammar.ANNOTATIONS:
                if i + 1 < len(interpretation):
                    if isinstance(interpretation[i + 1], list):
                        builder.append(self.make_uncertainty_regex(token, uncertainty, interpretation[i + 1]))
                        i += 2
                        continue

            builder.append(self.make_uncertainty_regex(token, uncertainty))
            i += 1

        if self.search_mode is SearchMode.CONTAIN:
            builder.append(".*")

        if self.search_mode is SearchMode.MATCH or \
                self.search_mode is SearchMode.CONTAIN:
            builder.append(r"(?:\Z|\s)")

        return "".join(builder)

    def get_starting_letters(self, interpretations: List[Interpretation]) -> Set[str]:
        """Get a set of starting letters based on the given interpretations
        factoring in uncertainty.
        
        :param interpretations: A list of interpretations to generate 
            starting letters for.
        :returns: A set of characters.
        """

        if self.search_mode is SearchMode.CONTAIN:
            return grammar.HARD_CHARACTERS

        letters = set()
        for interp in interpretations:
            for token in interp:
                if token[0] in grammar.HARD_CHARACTERS:
                    if self.fix_first:
                        strokes = get_similar(token, 0)
                    else:
                        strokes = get_similar(token, self.uncertainty)
                    flattened_strokes = list()
                    for tup in strokes:
                        flattened_strokes += [s for s in tup]
                    letters |= set(string[0] for string in flattened_strokes)
                    break

        return letters

    def generate_patterns(self, interpretations: List[Interpretation]) -> List[Pattern]:
        """Generates a set of compiled regular expressions from a list
        of interpretations.
        
        :param interpretations: A list of interpretations to generate 
            patterns for.
        :returns: A list of Patterns.
        """

        patterns = list()
        for interp in interpretations:
            regex = self.build_regex(interp)
            # print(regex)
            patterns.append(re.compile(regex))
        return patterns


    def generate_patterns_map(self, interpretations: List[Interpretation]) -> List[Tuple[Interpretation, Pattern]]:
        """Generates a set of compiled regular expressions from a list
        of interpretations.
        
        :param interpretations: A list of interpretations to generate 
            patterns for.
        :returns: A list of Interpretations with their corresponding 
            Patterns.
        """

        patterns = list()
        for interp in interpretations:
            regex = self.build_regex(interp)
            # print(regex)
            # patterns.append(re.compile(regex))
            patterns.append((interp, re.compile(regex)))
        return patterns
