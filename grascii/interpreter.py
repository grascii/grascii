"""
:type Interpretation:
    Represents an interpretation of a Grascii string. An ``Interpretation`` is
    a list of strokes and annotation lists. Each stroke is its own element in
    the interpretation, while sequences of annotations are grouped into their
    own sublist.
"""

from __future__ import annotations

import re
from functools import reduce
from itertools import chain
from typing import List, Optional, Set, Union

from grascii import grammar
from grascii.validator import GrasciiValidator

Interpretation = List[Union[str, List[str]]]


def _get_annotation_set(stroke: str) -> Set[str]:
    """Get a set of all annotations allowed on the given stroke."""
    annotations = grammar.ANNOTATIONS.get(stroke, [])
    return set(chain(*annotations))


"""
A dictionary of multi-character strokes to exception patterns.
A matching sequence of characters in the Grascii string is treated as the
corresponding multi-character stroke unless following characters match the
exception pattern.
"""
_EXCEPTIONS = {
    "EU": "[).,]",
    "AU": "[).,]",
    "OE": "[~|,.]",
    "NT": "[HNM]",
    "ND": "[NM]",
    "MT": "[HNM]",
    "MD": "[NM]",
    "JNT": "[H]",
    "PNT": "[H]",
    "DT": "[H]",
    "SS": "H|[)(]?,",
    "XS": "H|[)(]?,",
}


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

        tokens = []
        i = 0
        while i < len(grascii):
            matched = False
            # try matching 3-character strokes and then 2-character strokes
            for size in range(3, 1, -1):
                if i + size <= len(grascii):
                    candidate = grascii[i : i + size]
                    if candidate in grammar.STROKES:
                        exception = _EXCEPTIONS.get(candidate)
                        # Make sure the following characters do not prevent a match
                        if (
                            not exception
                            or re.match(exception, grascii[i + size :]) is None
                        ):
                            matched = True
                            tokens.append(candidate)
                            i += size
                            break

            if not matched:
                # single-character stroke or other annotation or symbol
                if grascii[i] != grammar.BOUNDARY or preserve_boundaries:
                    tokens.append(grascii[i])
                i += 1

        return self._tokens_to_interpretation(tokens)

    def _tokens_to_interpretation(
        self,
        tokens: List[str],
    ) -> Interpretation:
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
