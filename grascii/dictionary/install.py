from __future__ import annotations

import argparse
import sys
from pathlib import Path
from shutil import copy
from typing import Optional

from grascii.dictionary.common import (
    INSTALLATION_DIR,
    DictionaryAlreadyExists,
    get_dictionary_installed_name,
    get_dictionary_path_name,
)

description = "Install a Grascii Dictionary"


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


def install_dictionary(
    dictionary: Path,
    install_dir: Path,
    name: Optional[str] = None,
    force: bool = False,
) -> str:
    """Install a dictionary to an installation directory.

    :param dictionary: A path to the output directory of a dictionary build.
    :param install_dir: A path to install the dictionary to.
    :param name: An optional name to give the installed dictionary.
    :param force: If True, an existing dictionary can be overwritten.
    :type dictionary: Path
    :type install_dir: Path
    :type name: str
    :type force: bool

    :returns: The installed name of the dictionary.
    """
    if name is None:
        name = dictionary.name
    else:
        name = get_dictionary_path_name(name)
    destination = install_dir / name
    if destination.exists() and not force:
        raise DictionaryAlreadyExists(name)
    destination.mkdir(parents=True, exist_ok=True)
    files = dictionary.glob("[A-Z]")
    for f in files:
        copy(f, destination)
    return get_dictionary_installed_name(name)


def cli_install(args: argparse.Namespace) -> None:
    try:
        name = install_dictionary(
            args.dictionary, INSTALLATION_DIR, args.name, args.force
        )
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
