#!/usr/bin/env python

import sys
import argparse

import build_dict as build
import search

def no_command(args):
    print("Expecting subcommand")
    print("For help run:")
    print("grascii.py --help")

def main(arguments):

    argparser = argparse.ArgumentParser()
    argparser.set_defaults(func=no_command)
    subparsers = argparser.add_subparsers(title="subcommands")   

    search_parser = subparsers.add_parser("search", 
            description=search.description, 
            help=search.description,
            aliases=["s"])
    search.build_argparser(search_parser)
    search_parser.set_defaults(func=search.main)

    build_parser = subparsers.add_parser("build", 
            description=build.description, 
            help=build.description,
            aliases=["b"])
    build.build_argparser(build_parser)
    build_parser.set_defaults(func=build.main)

    args = argparser.parse_args(arguments)

    args.func(args)

if __name__ == "__main__":
    main(sys.argv[1:])

