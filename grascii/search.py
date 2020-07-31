"""
Acts as the main entry point for the grascii search command.

This can be invoked as a standalone program:
$ python -m grascii.search --help
"""

import argparse
from configparser import ConfigParser
import io
import os
import re
import sys
from typing import Union, List, Dict, Set, Iterable, Match, Pattern, cast, Optional

from grascii import regen, defaults
from grascii.searchers import GrasciiSearcher, RegexSearcher, ReverseSearcher, Searcher
from grascii.interactive import InteractiveSearcher

description = "Search a Grascii Dictionary"

def build_argparser(argparser: argparse.ArgumentParser) -> None:
    """Configure an ArgumentParser parser to parse the search command-line
    options.
    
    :param argparser: A fresh ArgumentParser to configure.
    """

    group = argparser.add_mutually_exclusive_group(required=True)
    group.add_argument("-g", "--grascii", 
            help="the grascii string to search for")
    group.add_argument("-e", "--regexp", 
            help="a custom regular expression to use in the search")
    group.add_argument("-r", "--reverse", 
            help="search by word instead")
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
    """Set defaults for arguments that were unprovided.

    :param args: The set of arguments to process.
    """

    # conf = ConfigParser()
    # conf.read("grascii.conf")
    # uncertainty = defaults.SEARCH.getint("Uncertainty")
    # uncertainty = max(0, min(uncertainty, 2))
    # search_mode = defaults.SEARCH["SearchMode"]
    # annotation_mode = defaults.SEARCH["AnnotationMode"]
    # aspirate_mode = defaults.SEARCH["AspirateMode"]
    # disjoiner_mode = defaults.SEARCH["DisjoinerMode"]
    # interpretation = defaults.SEARCH["Interpretation"]

    # if args.uncertainty is None:
        # args.uncertainty = uncertainty
    # if args.search_mode is None:
        # args.search_mode = search_mode
    # if args.annotation_mode is None:
        # args.annotation_mode = annotation_mode
    # if args.aspirate_mode is None:
        # args.aspirate_mode = aspirate_mode
    # if args.disjoiner_mode is None:
        # args.disjoiner_mode = disjoiner_mode
    # if args.interpretation is None:
        # args.interpretation = interpretation

    # args.search_mode = regen.SearchMode(args.search_mode)
    # args.annotation_mode = regen.Strictness(args.annotation_mode)
    # args.aspirate_mode = regen.Strictness(args.aspirate_mode)
    # args.disjoiner_mode = regen.Strictness(args.disjoiner_mode)

    # args.dict_path = conf.get("Search", "DictionaryPath", 
            # fallback=defaults.SEARCH["DictionaryPath"])

def search(**kwargs) -> Optional[Iterable[str]]:
    """Run a grascii dictionary search. Parameters can consist of
    any parameters used by the search method of any subclass of
    Searcher. One, and only one, of the parameters list below
    is required.

    :param grascii: A grascii string to use in a search.
    :param interactive: A flag enabling an interactive search.
    :param reverse: A word to search for in the dictionary.
    :param regexp: A regular expression to use in a search.
    :type grascii: str
    :type interactive: bool
    :type reverse: str
    :type regexp: str

    :returns: A list of search results, or None if run in interactive mode
    """

    searcher: Searcher
    if kwargs.get("grascii"):
        searcher = GrasciiSearcher()
    elif kwargs.get("interactive"):
        searcher = InteractiveSearcher()
    elif kwargs.get("reverse"):
        searcher = ReverseSearcher()
    else:
        searcher = RegexSearcher()
    return searcher.search(**kwargs)

def cli_search(args: argparse.Namespace) -> None:
    """Run a search using arguments parsed from the command line.
    
    :param args: A namespace of parsed arguments.
    """

    process_args(args)
    results = search(**{k: v for k, v in vars(args).items() if v is not None})
    count = 0
    for result in results:
        print(result.strip())
        count += 1
    print("Results:", count)

def main() -> None:
    """Run a search using arguments retrieved from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_search(args)
    search(**{k: v for k, v in vars(args).items() if v is not None})

if __name__ == "__main__":
    main()
