from __future__ import annotations

import argparse
import sys
from pathlib import Path
from shutil import rmtree

from grascii.dictionary.common import DictionaryNotFound, get_dictionary_path_name
from grascii.dictionary.install import DICTIONARY_PATH

description = "Uninstall a Grascii Dictionary"


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    argparser.add_argument(
        "name", action="store", help="The name of the dictionary to uninstall"
    )
    argparser.add_argument(
        "-f", "--force", action="store_true", help="Force removal of a dictionary"
    )


def uninstall_dictionary(
    name: str, directory: Path = DICTIONARY_PATH, force: bool = False
) -> None:
    dictionary_path = directory / get_dictionary_path_name(name)
    if not dictionary_path.exists():
        raise DictionaryNotFound(get_dictionary_path_name(name))
    if force:
        rmtree(dictionary_path)
    else:
        for f in dictionary_path.iterdir():
            f.unlink()
        dictionary_path.rmdir()


def cli_uninstall(args: argparse.Namespace) -> None:
    try:
        uninstall_dictionary(args.name, force=args.force)
    except DictionaryNotFound:
        print(args.name, "does not exist.", file=sys.stderr)
    except OSError:
        print("An error occurred during uninstallation.", file=sys.stderr)
        print("The dictionary may be corrupted.", file=sys.stderr)
        print("To force removal, run with --force.", file=sys.stderr)
    else:
        print("Successfully uninstalled", args.name)


def main() -> None:
    """Run the uninstall command using arguments from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_uninstall(args)


if __name__ == "__main__":
    main()
