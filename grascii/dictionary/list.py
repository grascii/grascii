
import argparse
from pathlib import Path, PurePath
from shutil import copy
import sys

from pkg_resources import resource_listdir, resource_isdir

from grascii.dictionary.install import DICTIONARY_PATH

description = "List built-in and installed dictionaries."

def build_argparser(argparser: argparse.ArgumentParser) -> None:
    return

def cli_list(args: argparse.Namespace) -> None:
    print("Built-in Dictionaries:")
    files = resource_listdir("grascii", "dictionary")
    for f in files:
        if resource_isdir("grascii.dictionary", f) and f[0] != "_":
            print(f)
    print()

    print("Installed Dictionaries:")
    if DICTIONARY_PATH.exists():
        for f in DICTIONARY_PATH.iterdir():
            if f.is_dir():
                print(f.name)

def main() -> None:
    """Run the list command using arguments from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_list(args)

if __name__ == "__main__":
    main()
