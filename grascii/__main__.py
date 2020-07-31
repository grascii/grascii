#!/usr/bin/env python

import sys
import argparse
import os

from grascii import search, build, config

def no_command(args: argparse.ArgumentParser) -> None:
    print("Expecting subcommand")
    print("For help run:")
    print("grascii.py --help")

def main() -> None:
    argparser = argparse.ArgumentParser(prog="grascii")
    argparser.set_defaults(func=no_command)
    subparsers = argparser.add_subparsers(title="subcommands")   

    search_parser = subparsers.add_parser("search", 
            description=search.description, 
            help=search.description,
            aliases=["s"])
    search.build_argparser(search_parser)
    search_parser.set_defaults(func=search.cli_search)

    build_parser = subparsers.add_parser("build", 
            description=build.description, 
            help=build.description,
            aliases=["b"])
    build.build_argparser(build_parser)
    build_parser.set_defaults(func=build.cli_build)

    config_parser = subparsers.add_parser("config", 
            description=config.description, 
            help=config.description,
            aliases=["cf"])
    config.build_argparser(config_parser)
    config_parser.set_defaults(func=config.cli_config)

    args = argparser.parse_args(sys.argv[1:])

    args.func(args)

if __name__ == "__main__":
    main()

