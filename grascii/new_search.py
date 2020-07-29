from abc import ABC, abstractmethod
from functools import reduce
from typing import Union, List, Set, Iterable, Dict, TypeVar, Callable, Pattern, Tuple, Match

from lark import Lark, Tree, UnexpectedInput, Transformer, Token
from lark.visitors import CollapseAmbiguities

from grascii import regen, utils, metrics, grammar
from grascii.grammars import get_grammar

Interpretation = Union[str, List[str]]

class GrasciiFlattener(Transformer):

    def start(self, children):
        result = list()
        for child in children:
            for token in child:
                if token in grammar.ANNOTATION_CHARACTERS:
                    if isinstance(result[-1], list):
                        result[-1].append(token)
                    else:
                        result.append([token])
                else:
                    result.append(token)
        return result

    def group_modifiers(self, children):
        return children[0], set(children[1:])

    def __default__(self, data, children, meta):
        result = list()
        for child in children:
            if isinstance(child, Token):
                result.append(child)
            else:
                for token in child:
                    result.append(token)
        return result

T = TypeVar("T")

class Searcher(ABC):

    def __init__(self, **kwargs):
        self.dictionary = ":preanniversary"

    def perform_search(self, patterns: Iterable[Tuple[T, Pattern]], starting_letters: Set[str], metric: Callable[[T, Match], int]) -> Iterable[str]:
        sorted_results: List[Tuple[str, int]] = list()
        for item in sorted(starting_letters):
            try:
                with utils.get_dict_file(self.dictionary, item) as dictionary:
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

    # @abstractmethod
    # def search(self, ...):
        # ...

class GrasciiSearcher(Searcher):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        grammar = get_grammar("grascii")
        self.parser = Lark(grammar, parser="earley", ambiguity="explicit") 

    def parse_grascii(self, grascii: str) -> Union[Tree, bool]:
        try:
            return self.parser.parse(grascii)
        except UnexpectedInput as e:
            # print("Syntax Error")
            # print(e.get_context(grascii))
            return False

    def flatten_tree(self, parse_tree: Tree) -> List[Interpretation]:
        trees = CollapseAmbiguities().transform(parse_tree)
        trans = GrasciiFlattener()
        return [trans.transform(tree) for tree in trees]

    def interpretation_to_string(self, interp: Interpretation) -> str:
        def reducer(builder, token):
            if isinstance(token, list):
                builder += token
            else:
                if builder and builder[-1] != "^" and token != "^":
                    builder.append("-")
                builder.append(token)
            return builder

        return "".join(reduce(reducer, interp, []))

    def get_unique_interpretations(self, interpretations: List[Interpretation]) -> Dict[str, Interpretation]:
        return {self.interpretation_to_string(interp): interp for interp in interpretations}

    # def perform_search(self, patterns, starting_letters: Set[str]) -> Iterable[str]:
        # sorted_results = list()
        # for item in sorted(starting_letters):
            # try:
                # with utils.get_dict_file(self.dictionary, item) as dictionary:
                    # for line in dictionary:
                        # m = False
                        # metric = 2^32 - 1
                        # for interp, pattern in patterns:
                            # match = pattern.search(line)
                            # if match:
                                # m = True
                                # metric = min(metric, metrics.standard(interp, match))
                        # if m:
                            # i = len(sorted_results)
                            # sorted_results.append((line, metric))
                            # while i > 0:
                                # if sorted_results[i][1] < sorted_results[i - 1][1]:
                                    # tmp = sorted_results[i - 1]
                                    # sorted_results[i - 1] = sorted_results[i]
                                    # sorted_results[i] = tmp
                                # i -= 1
            # except FileNotFoundError:
                # pass
                # # print("Error: Could not find", dict_path + item)
        # for tup in sorted_results:
            # yield tup[0]

    def search(self, **kwargs):
        grascii = kwargs["grascii"].upper()
        self.uncertainty = kwargs.get("uncertainty", 0)
        # handle enum conversion error?
        self.search_mode = regen.SearchMode(kwargs.get("search_mode", "match"))
        self.annotation_mode = regen.Strictness(kwargs.get("annotation_mode", "discard"))
        self.aspirate_mode = regen.Strictness(kwargs.get("aspirate_mode", "discard"))
        self.disjoiner_mode = regen.Strictness(kwargs.get("disjoiner_mode", "strict"))
        self.fix_first = kwargs.get("fix_first", False)
        self.interpretation_mode = kwargs.get("interpretation", "best")

        tree = self.parse_grascii(grascii)
        if not tree:
            raise Exception
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

