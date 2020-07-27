
from functools import reduce
import re
import sys
import argparse
import io
import os
from configparser import ConfigParser
from typing import Union, List, Dict, Set, Iterable, Match, Pattern, cast

from lark import Lark, Visitor, Transformer, Discard, Token, UnexpectedInput, Tree
from lark.visitors import CollapseAmbiguities

from grascii import regen, grammar, defaults, utils

vprint = lambda *a, **k: None

description = "Search a Grascii Dictionary"

def build_argparser(argparser: argparse.ArgumentParser) -> None:
    group = argparser.add_mutually_exclusive_group(required=True)
    group.add_argument("-g", "--grascii", 
            help="the grascii string to search for")
    group.add_argument("-r", "--regex", 
            help="a custom regular expression to use in the search")
    group.add_argument("-i", "--interactive", action="store_true",
            help="run in interactive mode")
    argparser.add_argument("-u", "--uncertainty", type=int, choices=range(3),
            help="the uncertainty of the search term")
    argparser.add_argument("-s", "--search-mode",
            choices=[mode.value for mode in regen.SearchMode],
            help="the kind of search to perform")
    argparser.add_argument("-a", "--annotation-mode",
            choices=[mode.value for mode in regen.Strictness],
            help="how to handle annotations in grascii")
    argparser.add_argument("-p", "--aspirate-mode",
            choices=[mode.value for mode in regen.Strictness],
            help="how to handle aspirates in grascii")
    argparser.add_argument("-j", "--disjoiner-mode",
            choices=[mode.value for mode in regen.Strictness],
            help="how to handle disjoiners in grascii")
    argparser.add_argument("-n", "--interpretation", 
            choices=["best", "all"],
            help="how to handle ambiguous grascii strings")
    argparser.add_argument("-f", "--fix-first", action="store_true",
            help="apply an uncertainty of 0 to the first token")
    argparser.add_argument("-v", "--verbose", action="store_true",
            help="turn on verbose output")

class GrasciiFlattener(Transformer):

    # def __init__(self):
        # self.circle_vowel = self.group_modifiers
        # self.hook_vowel = self.group_modifiers
        # self.diphthong = self.group_modifiers
        # self.directed_consonant = self.group_modifiers
        # self.sh = self.group_modifiers

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

def create_parser(ambiguity: bool=True) -> Lark:
    grammar = utils.get_grammar("grascii")
    am = "explicit" if ambiguity else "resolve"
    return Lark(grammar, parser="earley", ambiguity=am)

def parse_grascii(parser: Lark, grascii: str) -> Union[Tree, bool]:
    try:
        return parser.parse(grascii)
    except UnexpectedInput as e:
        print("Syntax Error")
        print(e.get_context(grascii))
        return False

def flatten_tree(parse_tree: Tree) -> list:
    trees = CollapseAmbiguities().transform(parse_tree)
    trans = GrasciiFlattener()
    return [trans.transform(tree) for tree in trees]

def interpretation_to_string(interp: list) -> str:
    def reducer(builder, token):
        if isinstance(token, list):
            builder += token
        else:
            if builder and builder[-1] != "^" and token != "^":
                builder.append("-")
            builder.append(token)
        return builder

    return "".join(reduce(reducer, interp, []))

def get_unique_interpretations(flattened_parses: Iterable[list]) -> Dict[str, List[list]]:

    return {interpretation_to_string(interp): interp for interp in flattened_parses}

def perform_search(patterns: Iterable[Pattern], starting_letters: Set[str], dict_path) -> Iterable[str]:
    for item in sorted(starting_letters):
        try:
            with utils.get_dict_file(":preanniversary", item) as dictionary:
                for line in dictionary:
                    for pattern in patterns:
                        match = pattern.search(line)
                        if match:
                            print(match.groups())
                            yield line
                            break
        except FileNotFoundError:
            print("Error: Could not find", dict_path + item)

def process_args(args: argparse.Namespace) -> None:
    conf = ConfigParser()
    conf.read("grascii.conf")
    uncertainty = conf.getint('Search', 'Uncertainty', 
            fallback=defaults.SEARCH["Uncertainty"])
    uncertainty = max(0, min(uncertainty, 2))
    search_mode = conf.get('Search', "SearchMode", 
            fallback=defaults.SEARCH["SearchMode"])
    annotation_mode = conf.get('Search', "AnnotationMode", 
            fallback=defaults.SEARCH["AnnotationMode"])
    aspirate_mode = conf.get('Search', "AspirateMode", 
            fallback=defaults.SEARCH["AspirateMode"])
    disjoiner_mode = conf.get('Search', "DisjoinerMode", 
            fallback=defaults.SEARCH["DisjoinerMode"])
    interpretation = conf.get('Search', "Interpretation",
            fallback=defaults.SEARCH["Interpretation"])

    if args.uncertainty is None:
        args.uncertainty = uncertainty
    if args.search_mode is None:
        args.search_mode = search_mode
    if args.annotation_mode is None:
        args.annotation_mode = annotation_mode
    if args.aspirate_mode is None:
        args.aspirate_mode = aspirate_mode
    if args.disjoiner_mode is None:
        args.disjoiner_mode = disjoiner_mode
    if args.interpretation is None:
        args.interpretation = interpretation

    args.search_mode = regen.SearchMode(args.search_mode)
    args.annotation_mode = regen.Strictness(args.annotation_mode)
    args.aspirate_mode = regen.Strictness(args.aspirate_mode)
    args.disjoiner_mode = regen.Strictness(args.disjoiner_mode)

    args.dict_path = conf.get("Search", "DictionaryPath", 
            fallback=defaults.SEARCH["DictionaryPath"])

def search(args: argparse.Namespace) -> None:

    process_args(args)

    global vprint
    vprint = print if args.verbose else lambda *a, **k: None

    if args.interactive:
        from grascii import interactive
        vprint("Running in interactive mode")
        p = create_parser(ambiguity=True)
        interactive.run_interactive(p, args)
        exit(0)
    elif args.grascii is None:
        vprint("searching with custom regular expression:", args.regex.upper())
        patterns = [re.compile(args.regex.upper())]
        starting_letters = grammar.HARD_CHARACTERS
    else:
        p = create_parser(ambiguity=args.interpretation == "all")
        vprint("parsing grascii", args.grascii.upper())
        tree = parse_grascii(p, args.grascii.upper())
        if not tree:
            vprint("parsing failed")
            vprint("exiting")
            exit()
        tree = cast(Tree, tree)

        parses = flatten_tree(tree)
        vprint(tree.pretty())
        vprint(parses)
        display_interpretations = get_unique_interpretations(parses)
        interpretations = list(display_interpretations.values())
        vprint(interpretations)

        if args.interpretation == "best":
            assert len(interpretations) == 1

        builder = regen.RegexBuilder(args.uncertainty, args.search_mode, args.fix_first, args.annotation_mode, args.aspirate_mode, args.disjoiner_mode)
        interps = interpretations[0:1] if args.interpretation == "best" else interpretations
        patterns = builder.generate_patterns(interps)
        starting_letters = builder.get_starting_letters(interps)

    results = perform_search(patterns, starting_letters, args.dict_path)
    count = 0
    for result in results:
        print(result.strip())
        count += 1
    print("Results:", count)

def cli_search(args: argparse.Namespace) -> None:
    search(args)
    # search(**{k: v for k, v in vars(args).items() if v is not None})

def main() -> None:
    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    search(**{k: v for k, v in vars(args).items() if v is not None})

if __name__ == "__main__":
    main()
