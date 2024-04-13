"""
Acts as the main entry point for the grascii search command.

This can be invoked as a standalone program:
$ python -m grascii.search --help
"""

from __future__ import annotations

import argparse
import sys
from typing import Iterable, Optional

from grascii import regen
from grascii.dictionary import DictionaryNotFound
from grascii.parser import InvalidGrascii
from grascii.searchers import (
    GrasciiSearcher,
    RegexSearcher,
    ReverseSearcher,
    Searcher,
    SearchResult,
)

SUPPORTS_INTERACTIVE = False
try:
    from grascii.interactive import InteractiveSearcher

    SUPPORTS_INTERACTIVE = True
except ImportError:
    pass


description = "Search a Grascii Dictionary"


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    """Configure an ArgumentParser parser to parse the search command-line
    options.

    :param argparser: A fresh ArgumentParser to configure.
    """

    group = argparser.add_mutually_exclusive_group(required=True)
    group.add_argument("-g", "--grascii", help="the grascii string to search for")
    group.add_argument(
        "-e", "--regexp", help="a custom regular expression to use in the search"
    )
    group.add_argument("-r", "--reverse", help="search by word instead")
    group.add_argument(
        "-i", "--interactive", action="store_true", help="run in interactive mode"
    )
    argparser.add_argument(
        "-u",
        "--uncertainty",
        type=int,
        choices=range(3),
        help="the uncertainty of the search term",
    )
    argparser.add_argument(
        "-s",
        "--search-mode",
        choices=[mode.value for mode in regen.SearchMode],
        help="the kind of search to perform",
    )
    argparser.add_argument(
        "-a",
        "--annotation-mode",
        choices=[mode.value for mode in regen.Strictness],
        help="how to handle annotations in grascii",
    )
    argparser.add_argument(
        "-p",
        "--aspirate-mode",
        choices=[mode.value for mode in regen.Strictness],
        help="how to handle aspirates in grascii",
    )
    argparser.add_argument(
        "-j",
        "--disjoiner-mode",
        choices=[mode.value for mode in regen.Strictness],
        help="how to handle disjoiners in grascii",
    )
    argparser.add_argument(
        "-n",
        "--interpretation",
        choices=["best", "all"],
        help="how to handle ambiguous grascii strings",
    )
    argparser.add_argument(
        "-f",
        "--fix-first",
        action="store_true",
        help="apply an uncertainty of 0 to the first token",
    )
    argparser.add_argument(
        "-d",
        "--dictionary",
        dest="dictionaries",
        action="append",
        help="add a dictionary to be searched",
    )
    argparser.add_argument(
        "--no-sort",
        action="store_true",
        help="do not sort the search results",
    )


def search(**kwargs) -> Optional[Iterable[SearchResult]]:
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
        searcher = GrasciiSearcher(**kwargs)
    elif kwargs.get("interactive"):
        if not SUPPORTS_INTERACTIVE:
            print("The interactive extra is not installed", file=sys.stderr)
            return None
        searcher = InteractiveSearcher(**kwargs)
    elif kwargs.get("reverse"):
        searcher = ReverseSearcher(**kwargs)
    else:
        searcher = RegexSearcher(**kwargs)
    if kwargs.get("no_sort"):
        return searcher.search(**kwargs)
    return searcher.sorted_search(**kwargs)


def cli_search(args: argparse.Namespace) -> None:
    """Run a search using arguments parsed from the command line.

    :param args: A namespace of parsed arguments.
    """

    try:
        results = search(**{k: v for k, v in vars(args).items() if v is not None})
    except InvalidGrascii as e:
        print("Invalid Grascii String", file=sys.stderr)
        print(e.context, file=sys.stderr)
        return
    except DictionaryNotFound as e:
        print("Dictionary Not Found", file=sys.stderr)
        print(e.name, file=sys.stderr)
        return
    else:
        if results is not None:
            count = 0
            for result in results:
                print(result.entry.grascii, result.entry.translation)
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
