from functools import reduce
from pathlib import Path
from typing import List, Union

from lark import Lark, Token, Transformer, Tree, UnexpectedInput
from lark.visitors import CollapseAmbiguities

from grascii import APP_NAME, __version__, grammar
from grascii.appdirs import user_cache_dir
from grascii.grammars import get_grammar

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
    into an Interpretation. An Interpretation is a list of terminals and
    annotation lists. Each terminal is its own element in the interpretation,
    but sequences of annotation terminals are grouped into their own sublist.
    """

    def __init__(self, preserve_boundaries: bool = False) -> None:
        super().__init__()
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


_LALR_CACHE_DIR = (
    Path(user_cache_dir(appname=APP_NAME, version=__version__)) / "grammars"
)
_LALR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
_LALR_CACHE_FILE = _LALR_CACHE_DIR / "grascii.lark.cache"


class GrasciiValidator:
    def __init__(self, use_cache: bool = False) -> None:
        grammar = get_grammar("grascii")
        self._validator: Lark = Lark.open(
            grammar, parser="lalr", cache=str(_LALR_CACHE_FILE) if use_cache else False
        )

    def validate(self, grascii: str) -> bool:
        try:
            self._validator.parse(grascii)
            return True
        except UnexpectedInput:
            return False


class GrasciiParser:
    def __init__(self) -> None:
        grammar = get_grammar("grascii")
        self._parser: Lark = Lark.open(grammar, parser="earley", ambiguity="explicit")

    def parse(self, grascii: str) -> Tree:
        return self._parser.parse(grascii)

    def interpret(
        self, grascii: str, preserve_boundaries: bool = False
    ) -> List[Interpretation]:
        tree = self.parse(grascii)
        trees = CollapseAmbiguities().transform(tree)
        flattener = GrasciiFlattener(preserve_boundaries)
        interpretations = [flattener.transform(tree) for tree in trees]
        unique_interpretations = {
            interpretation_to_string(interp): interp for interp in interpretations
        }
        return list(unique_interpretations.values())
