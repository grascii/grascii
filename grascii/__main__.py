#!/usr/bin/env python

from __future__ import annotations

import argparse
import signal
import sys

from grascii import APP_NAME, __version__, config, dictionary, search


def main() -> None:
    try:
        from pytest_cov.embed import cleanup_on_signal
    except ImportError:
        pass
    else:
        cleanup_on_signal(signal.SIGHUP)

    argparser = argparse.ArgumentParser(prog=APP_NAME)
    subparsers = argparser.add_subparsers(title="subcommands")
    argparser.set_defaults(func=None)

    argparser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

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
