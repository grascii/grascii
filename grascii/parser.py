from __future__ import annotations

import re
from functools import lru_cache, reduce
from typing import Iterator, List, Union

from lark import Lark, Token, Transformer, Tree, UnexpectedInput

from grascii import grammar
from grascii.lark_ambig_tools import Disambiguator

Interpretation = List[Union[str, List[str]]]


def interpretation_to_string(interpretation: Interpretation) -> str:
    """Generate a string representation of an Interpretation.

    :param interpretation: An Interpretation to generate a string for.
    :returns: A string representation of an Interpretation
    """

    def reducer(builder, token):
        if isinstance(token, list):
            builder += token
        else:
            if (
                builder
                and builder[-1] != grammar.DISJOINER
                and token != grammar.DISJOINER
                and builder[-1] != grammar.BOUNDARY
                and token != grammar.BOUNDARY
            ):
                builder.append(grammar.BOUNDARY)
            if token != grammar.BOUNDARY:
                builder.append(token)
        return builder

    return "".join(reduce(reducer, interpretation, []))


class GrasciiFlattener(Transformer):

    """This is a Lark Transformer that converts a parsed Grascii string
    into an ``Interpretation``. An ``Interpretation`` is a list of terminals and
    annotation lists. Each terminal is its own element in the interpretation,
    but sequences of annotation terminals are grouped into their own sublist.
    """

    def __init__(
        self, preserve_boundaries: bool = False, start_rule: str = "start"
    ) -> None:
        super().__init__()
        setattr(self, start_rule, self.start)
        self.preserve_boundaries = preserve_boundaries

    def start(self, children) -> Interpretation:
        """Returns the final result of the transformation.

        :meta private:
        """

        result: Interpretation = []
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
                elif token != grammar.BOUNDARY or self.preserve_boundaries:
                    result.append(token)
        return result

    def __default__(self, data, children, meta) -> List[str]:
        """The default visitor function for nodes in the parse tree.
        Returns a flat list of strings."""

        result: List[str] = []
        for child in children:
            if isinstance(child, Token):
                result.append(child)
            else:
                # flatten iterable
                for token in child:
                    result.append(token)
        return result


@lru_cache(maxsize=1)
def get_grascii_regex_str() -> str:
    """Get a string that can be compiled into a regular expression that matches
    Grascii strings.
    """
    parser = Lark.open_from_package("grascii.grammars", "grascii_regex.lark")
    return parser.get_terminal("GRASCII").pattern.value


class GrasciiValidator:
    """Validates Grascii strings.

    :param ignore_case: Whether to ignore the case of the Grascii string. If
        ``False``, the Grascii string must be uppercase.
    :type ignore_case: bool
    """

    def __init__(self, ignore_case: bool = False) -> None:
        self._regex = re.compile(get_grascii_regex_str(), re.I if ignore_case else 0)

    def validate(self, grascii: str) -> bool:
        """Check whether the given string is valid Grascii.

        :param grascii: A string to check
        :returns: bool
        """
        return bool(self._regex.fullmatch(grascii))


class InvalidGrascii(Exception):
    """Exception thrown by the ``GrasciiParser`` when provided an invalid string."""

    def __init__(self, grascii: str, unexpected_input: UnexpectedInput) -> None:
        self.grascii = grascii
        self.unexpected_input = unexpected_input
        self.context = unexpected_input.get_context(grascii)


class GrasciiParser:
    """Parses and interprets Grascii strings."""

    def __init__(self) -> None:
        self._parser: Lark = Lark.open_from_package(
            "grascii.grammars", "grascii.lark", parser="earley", ambiguity="explicit"
        )

    def parse(self, grascii: str) -> Tree:
        """Parse the given string into a ``Tree``.

        :param grascii: A Grascii string to parse.
        :returns: An ambiguous parse tree of the Grascii string.
        """
        try:
            return self._parser.parse(grascii)
        except UnexpectedInput as ui:
            raise InvalidGrascii(grascii, ui)

    def interpret(
        self, grascii: str, preserve_boundaries: bool = False
    ) -> Iterator[Interpretation]:
        """Interpret a Grascii string.

        :param grascii: A Grascii string to interpret
        :param preserve_boundaries: When ``False``, boundaries in the string ('-')
            are not included in the resulting interpretations.
        :returns: An iterator over interpretations.
        """
        tree = self.parse(grascii)
        trees = Disambiguator().visit(tree)
        flattener = GrasciiFlattener(preserve_boundaries)
        return map(flattener.transform, trees)
