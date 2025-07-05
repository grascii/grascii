from __future__ import annotations

from typing import Iterator, List

from lark import Lark, Token, Transformer, Tree, UnexpectedInput

from grascii import grammar
from grascii.interpreter import Interpretation
from grascii.lark_ambig_tools import Disambiguator


class GrasciiFlattener(Transformer):

    """A Lark Transformer that converts a parsed Grascii string into an
    ``Interpretation``."""

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
