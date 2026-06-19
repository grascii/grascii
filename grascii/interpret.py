"""
Acts as the main entry point for the grascii interpret command.

This can be invoked as a standalone program:
``$ python -m grascii.interpret --help``
"""

from __future__ import annotations

import argparse
import sys

from grascii import InvalidGrascii
from grascii.interpreter import interpretation_to_string
from grascii.outline import Outline
from grascii.parser import GrasciiParser

description = "Interpret Grascii strings"


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    """Configure an ArgumentParser parser to parse the interpret command-line
    options.

    :param argparser: A fresh ArgumentParser to configure.
    """
    argparser.add_argument("grascii", help="the grascii string to interpret")
    argparser.add_argument(
        "-a",
        "--annotate",
        action="store_true",
        help="annotate strokes with their implied directions",
    )
    argparser.add_argument(
        "--all",
        action="store_true",
        help="print all interpretations",
    )


def cli_interpret(args: argparse.Namespace) -> int:
    """Run interpretation using arguments parsed from the command line.

    :param args: A namespace of parsed arguments.
    :returns: A CLI exit code
    """
    parser = GrasciiParser()

    try:
        interpretations = parser.interpret(args.grascii.upper())
    except InvalidGrascii as e:
        print("Invalid Grascii String", file=sys.stderr)
        print(e.context, file=sys.stderr)
        return 1

    for interpretation in interpretations:
        if args.annotate:
            outline = Outline(interpretation)
            interpretation = outline.to_interpretation()
        print(interpretation_to_string(interpretation))
        if not args.all:
            break

    return 0


def main() -> None:
    """Run interpretation using arguments retrieved from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_interpret(args)


if __name__ == "__main__":
    main()
