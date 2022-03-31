from functools import reduce
from typing import Union, List

from lark import Lark, Tree, Transformer, Token
from lark.visitors import CollapseAmbiguities

from grascii import grammar
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
            if builder and builder[-1] != "^" and token != "^":
                builder.append("-")
            builder.append(token)
        return builder

    return "".join(reduce(reducer, interpretation, []))

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

class GrasciiParser():

    def __init__(self) -> None:
        grammar = get_grammar("grascii")
        self._parser: Lark = Lark.open(grammar, parser="earley", ambiguity="explicit")
        self._flattener: Transformer = GrasciiFlattener()
        self._collapser: Transformer = CollapseAmbiguities()

    def parse(self, grascii: str) -> Tree:
        return self._parser.parse(grascii)

    def interpret(self, grascii: str) -> List[Interpretation]:
        tree = self.parse(grascii)
        trees = self._collapser.transform(tree)
        interpretations = [self._flattener.transform(tree) for tree in trees]
        unique_interpretations = {interpretation_to_string(interp): interp for interp in interpretations}
        return list(unique_interpretations.values())
