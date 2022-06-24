#!/usr/bin/env python

import argparse
import sys

from grascii import config, dictionary, search


def main() -> None:
    argparser = argparse.ArgumentParser(prog="grascii")
    subparsers = argparser.add_subparsers(title="subcommands")
    argparser.set_defaults(func=None)

    search_parser = subparsers.add_parser(
        "search", description=search.description, help=search.description, aliases=["s"]
    )
    search.build_argparser(search_parser)
    search_parser.set_defaults(func=search.cli_search)

    dictionary_parser = subparsers.add_parser(
        "dictionary",
        description=dictionary.description,
        help=dictionary.description,
        aliases=["d"],
    )
    dictionary.build_argparser(dictionary_parser)

    config_parser = subparsers.add_parser(
        "config",
        description=config.description,
        help=config.description,
        aliases=["cf"],
    )
    config.build_argparser(config_parser)
    config_parser.set_defaults(func=config.cli_config)

    args = argparser.parse_args(sys.argv[1:])

    if args.func:
        args.func(args)
    else:
        argparser.print_help()


if __name__ == "__main__":
    main()
