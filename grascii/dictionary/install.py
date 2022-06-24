import argparse
import sys
from pathlib import Path
from shutil import copy

from grascii.appdirs import user_data_dir
from grascii.config import APP_NAME

description = "Install a Grascii Dictionary"

DICTIONARY_PATH = Path(user_data_dir(APP_NAME), "dictionaries")


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


def install_dict(src: Path, dest: Path) -> None:
    files = src.glob("[A-Z]")
    for f in files:
        copy(f, dest)


def cli_install(args: argparse.Namespace) -> None:
    if args.name:
        name = args.name
    else:
        name = args.dictionary.name

    dest = DICTIONARY_PATH / name
    if dest.exists() and not args.force:
        if not dest.is_dir():
            print()
            return
        print("A dictionary named", name, "already exists.", file=sys.stderr)
        print("Provide a different name with --name.", file=sys.stderr)
        print("If you would like to overwrite it, run with --force.", file=sys.stderr)
        return

    dest.mkdir(parents=True, exist_ok=True)
    install_dict(args.dictionary, dest)
    print("Successfully installed", args.dictionary, "as", name)


def main() -> None:
    """Run the install command using arguments from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_install(args)


if __name__ == "__main__":
    main()
