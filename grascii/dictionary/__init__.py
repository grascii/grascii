import argparse
import io
import sys
from pathlib import Path
from typing import TextIO

from pkg_resources import resource_exists, resource_stream

from grascii.dictionary import build, install
from grascii.dictionary import list as list_dict
from grascii.dictionary import uninstall
from grascii.dictionary.install import DICTIONARY_PATH

description = "Create and manage Grascii dictionaries"


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    argparser.set_defaults(func=list_dict.cli_list)
    subparsers = argparser.add_subparsers(title="subcommands")

    build_parser = subparsers.add_parser(
        "build", description=build.description, help=build.description, aliases=["b"]
    )
    build.build_argparser(build_parser)
    build_parser.set_defaults(func=build.cli_build)

    install_parser = subparsers.add_parser(
        "install",
        description=install.description,
        help=install.description,
        aliases=["i"],
    )
    install.build_argparser(install_parser)
    install_parser.set_defaults(func=install.cli_install)

    uninstall_parser = subparsers.add_parser(
        "uninstall",
        description=uninstall.description,
        help=uninstall.description,
        aliases=["u"],
    )
    uninstall.build_argparser(uninstall_parser)
    uninstall_parser.set_defaults(func=uninstall.cli_uninstall)

    list_parser = subparsers.add_parser(
        "list",
        description=list_dict.description,
        help=list_dict.description,
        aliases=["l"],
    )
    list_dict.build_argparser(list_parser)
    list_parser.set_defaults(func=list_dict.cli_list)


def get_dict_file(dictionary: str, name: str) -> TextIO:
    if dictionary[0] == ":":
        if resource_exists("grascii.dictionary", dictionary[1:]):
            module = "grascii.dictionary." + dictionary[1:]
            return io.TextIOWrapper(resource_stream(module, name), encoding="utf-8")
        directory = DICTIONARY_PATH.joinpath(dictionary[1:])
        if not directory.exists():
            print(dictionary, "does not exist.", file=sys.stderr)
        return directory.joinpath(name).open()
    return Path(dictionary, name).open()
