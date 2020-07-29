
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

from grascii import regen, grammar, defaults, utils, metrics
from grascii.new_search import GrasciiSearcher, RegexSearcher, ReverseSearcher
from grascii.interactive import InteractiveSearcher


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

def search(**kwargs) -> Iterable[str]:

    if kwargs.get("grascii"):
        return GrasciiSearcher().search(**kwargs)
    elif kwargs.get("interactive"):
        return InteractiveSearcher().search(**kwargs)
    return ReverseSearcher().search(**kwargs)

def cli_search(args: argparse.Namespace) -> None:
    process_args(args)
    results = search(**{k: v for k, v in vars(args).items() if v is not None})
    count = 0
    for result in results:
        print(result.strip())
        count += 1
    print("Results:", count)

def main() -> None:
    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_search(args)
    search(**{k: v for k, v in vars(args).items() if v is not None})

if __name__ == "__main__":
    main()
