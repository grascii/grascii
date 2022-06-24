import argparse
import sys
from typing import Collection

from pkg_resources import resource_isdir, resource_listdir

from grascii.dictionary.install import DICTIONARY_PATH

description = "List built-in and installed dictionaries."


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    return


def get_built_ins() -> Collection[str]:
    files = resource_listdir("grascii", "dictionary")
    built_ins = filter(
        lambda f: resource_isdir("grascii.dictionary", f) and f[0] != "_", files
    )
    return list(built_ins)


def get_installed() -> Collection[str]:
    if DICTIONARY_PATH.exists():
        files = filter(lambda f: f.is_dir(), DICTIONARY_PATH.iterdir())
        installed = map(lambda f: f.name, files)
        return list(installed)
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
