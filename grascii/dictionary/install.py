from __future__ import annotations

import argparse
import sys
from pathlib import Path
from shutil import copy
from typing import Optional

from grascii.appdirs import user_data_dir
from grascii.config import APP_NAME

description = "Install a Grascii Dictionary"

DICTIONARY_PATH = Path(user_data_dir(APP_NAME), "dictionaries")


class DictionaryAlreadyExists(Exception):
    def __init__(self, name: str) -> None:
        self.name = name


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    argparser.add_argument(
        "-n",
        "--name",
        action="store",
        help="The name to give to the installed dictionary.",
    )
    argparser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Allow overwriting of an existing installed dictionary.",
    )
    argparser.add_argument(
        "dictionary",
        action="store",
        type=Path,
        help="Path to the built dictionary to install.",
    )


def install_dict(
    src: Path,
    dest: Path = DICTIONARY_PATH,
    name: Optional[str] = None,
    force: bool = False,
) -> str:
    if name is None:
        name = src.name
    installation_dir = dest / name
    if installation_dir.exists() and not force:
        raise DictionaryAlreadyExists(name)
    installation_dir.mkdir(parents=True, exist_ok=True)
    files = src.glob("[A-Z]")
    for f in files:
        copy(f, installation_dir)
    return ":" + name


def cli_install(args: argparse.Namespace) -> None:
    try:
        name = install_dict(args.dictionary, DICTIONARY_PATH, args.name, args.force)
    except DictionaryAlreadyExists as e:
        print("A dictionary named", e.name, "already exists.", file=sys.stderr)
        print("Provide a different name with --name.", file=sys.stderr)
        print("If you would like to overwrite it, run with --force.", file=sys.stderr)
    else:
        print("Successfully installed", args.dictionary, "as", name)


def main() -> None:
    """Run the install command using arguments from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_install(args)


if __name__ == "__main__":
    main()
