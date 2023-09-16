from __future__ import annotations

import argparse
import sys
from typing import Collection

from grascii.dictionary.common import INSTALLATION_DIR, get_dictionary_installed_name

description = "List built-in and installed dictionaries."


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    return


def get_built_ins() -> Collection[str]:
    """Get a collection of the installed names of all built-in dictionaries.

    :returns: A collection of built-in dictionary names.
    """
    if sys.version_info >= (3, 9):
        from importlib.resources import files
    else:
        from importlib_resources import files
    entries = files("grascii.dictionary").iterdir()
    built_ins = filter(lambda e: e.is_dir() and e.name[0] != "_", entries)
    return list(map(lambda e: get_dictionary_installed_name(e.name), built_ins))


def get_installed() -> Collection[str]:
    """Get a collection of the installed names of all user-installed dictionaries.

    :returns: A collection of installed dictionary names.
    """
    if INSTALLATION_DIR.exists():
        files = filter(lambda f: f.is_dir(), INSTALLATION_DIR.iterdir())
        installed = map(lambda f: f.name, files)
        return list(map(get_dictionary_installed_name, installed))
    return []


def cli_list(args: argparse.Namespace) -> None:
    print("Built-in Dictionaries:")
    for built_in in get_built_ins():
        print(built_in)
    print()

    print("Installed Dictionaries:")
    for installed in get_installed():
        print(installed)


def main() -> None:
    """Run the list command using arguments from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_list(args)


if __name__ == "__main__":
    main()
