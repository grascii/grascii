import argparse
import sys
from shutil import rmtree

from grascii.dictionary.install import DICTIONARY_PATH

description = "Uninstall a Grascii Dictionary"


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    argparser.add_argument(
        "name", action="store", help="The name of the dictionary to uninstall"
    )
    argparser.add_argument(
        "-f", "--force", action="store_true", help="Force removal of a dictionary"
    )


def uninstall_dict(name: str, force: bool = False) -> None:
    dictionary = DICTIONARY_PATH / name
    if force:
        rmtree(dictionary)
    else:
        for f in dictionary.iterdir():
            f.unlink()
        dictionary.rmdir()


def cli_uninstall(args: argparse.Namespace) -> None:
    dictionary = DICTIONARY_PATH / args.name
    if not dictionary.exists():
        print(args.name, "does not exist.", file=sys.stderr)
        return
    if not dictionary.is_dir():
        return

    try:
        uninstall_dict(args.name, args.force)
        print("Successfully uninstalled", args.name)
    except Exception:
        print("An error occurred during uninstallation.", file=sys.stderr)
        print("The dictionary may be corrupted.", file=sys.stderr)
        print("To force removal, run with --force.", file=sys.stderr)


def main() -> None:
    """Run the uninstall command using arguments from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_uninstall(args)


if __name__ == "__main__":
    main()
