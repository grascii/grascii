"""
:type Interpretation:
    Represents an interpretation of a Grascii string. An ``Interpretation`` is
    a list of strokes and annotation lists. Each stroke is its own element in
    the interpretation, while sequences of annotations are grouped into their
    own sublist.
"""

from __future__ import annotations

from functools import reduce
from itertools import chain
from typing import List, Optional, Set, Tuple, Union

from grascii import grammar
from grascii.validator import GrasciiValidator

Interpretation = List[Union[str, List[str]]]


def _get_annotation_set(stroke: str) -> Set[str]:
    """Get a set of all annotations allowed on the given stroke."""
    annotations = grammar.ANNOTATIONS.get(stroke, [])
    return set(chain(*annotations))


"""
A list of prioritized groups of character replacements. Each element in a group
contains a list of characters that make up a multi-character token and a set of
exception annotations. A matching sequence of characters in the Grascii string
is replaced by the corresponding multi-character token unless the following
character is contained in the exception set.
"""
_replacements: List[List[Tuple[List[str], Set[str]]]] = [
    [
        (["C", "H"], set()),
        (["S", "H"], set()),
        (["T", "H"], set()),
        (["A", "&", "'"], set()),
        (["A", "&", "E"], set()),
        (["M", "N"], set()),
        (["M", "M"], set()),
        (["E", "U"], _get_annotation_set("U") - _get_annotation_set("EU")),
        (["A", "U"], _get_annotation_set("U") - _get_annotation_set("AU")),
        (["O", "E"], _get_annotation_set("E") - _get_annotation_set("OE")),
    ],
    [
        (["J", "N", "T"], set()),
        (["J", "N", "D"], set()),
        (["P", "N", "T"], set()),
        (["P", "N", "D"], set()),
        (["S", "S"], _get_annotation_set("S") - _get_annotation_set("SS")),
        (["X", "S"], _get_annotation_set("S") - _get_annotation_set("XS")),
    ],
    [
        (["T", "N"], set()),
        (["D", "N"], set()),
        (["T", "M"], set()),
        (["D", "M"], set()),
        (["N", "G"], set()),
        (["N", "K"], set()),
    ],
    [
        (["N", "T"], set()),
        (["N", "D"], set()),
        (["M", "T"], set()),
        (["M", "D"], set()),
        (["T", "D"], set()),
        (["D", "T"], set()),
        (["D", "D"], set()),
        (["D", "F"], set()),
        (["D", "V"], set()),
        (["T", "V"], set()),
        (["L", "D"], set()),
    ],
]


class GrasciiInterpreter:
    """Produces the canonical interpretation of Grascii strings.

    ``GrasciiInterpreter.interpret`` is an alternative to
    ``GrasciiParser.interpret``. Use ``GrasciiParser`` when interpretations
    beyond the canonical interpretation are required, or improved error messages
    for invalid Grascii strings are desired. Otherwise, use ``GrasciiInterpreter``
    for better performance.
    """

    def __init__(self):
        self.validator = GrasciiValidator()

    def interpret(
        self, grascii: str, preserve_boundaries: bool = False
    ) -> Optional[Interpretation]:
        """Determine the canonical interpretation of the provided Grascii string.

        :param grascii: A Grascii string to interpret
        :param preserve_boundaries: When ``False``, boundaries in the string ('-')
            are not included in the resulting interpretation.
        :returns: The canonical interpretation or ``None`` if the string is not
            valid Grascii.
        """
        if not self.validator.validate(grascii):
            return None

        # From here on, grascii is known to be valid, so our interpreting logic
        # does not need to be as complex as if we had to account for invalid strings.
        # For instance, we don't need to check for invalid characters or
        # invalid usages of annotations.

        current = list(grascii)

        for group in _replacements:
            next = []

            i = 0
            while i < len(current):
                matched = False
                for replacement, exceptions in group:
                    end = i + len(replacement)
                    is_match = end <= len(current) and replacement == current[i:end]
                    no_exception = end >= len(current) or current[end] not in exceptions
                    matched = is_match and no_exception
                    if matched:
                        next.append("".join(replacement))
                        i += len(replacement)
                        break

                if not matched:
                    if preserve_boundaries or current[i] != grammar.BOUNDARY:
                        next.append(current[i])
                    i += 1

            current = next

        return self._tokens_to_interpretation(current)

    def _tokens_to_interpretation(self, tokens: List[str]) -> Interpretation:
        interpretation: Interpretation = []
        annotations: List[str] = []

        for token in tokens:
            if token in grammar.ANNOTATION_CHARACTERS:
                if annotations:
                    annotations.append(token)
                else:
                    annotations = [token]
            else:
                if annotations:
                    interpretation.append(annotations)
                    annotations = []
                interpretation.append(token)

        if annotations:
            interpretation.append(annotations)

        return interpretation


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
