"""Contains functions for working with a grascii configuration file.
Acts as the entry point for the grascii config command.

This can be invoked as a standalone program:
$ python -m grascii.config --help
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path, PurePath

from platformdirs import user_config_dir

from grascii import APP_NAME

CONF_DIRECTORY = user_config_dir(APP_NAME)
CONF_FILE_NAME = APP_NAME + ".conf"
DEFAULTS_CONF_NAME = "defaults.conf"

description = "Manage Grascii configuration"


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    """Configure an ArgumentParser parser to parse the config command-line
    options

    :parse argparser: A fresh ArgumentParser to configure.
    """

    group = argparser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--init", action="store_true", help="Create a configuration file."
    )
    group.add_argument(
        "-D",
        "--delete",
        action="store_true",
        help="Delete an existing configuration file.",
    )
    group.add_argument(
        "-w",
        "--where",
        action="store_true",
        help="Print the path to the configuration file and exit.",
    )
    argparser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Allow overwriting of an existing configuration file.",
    )


def get_default_config() -> str:
    """Get the text of the default configuration file.

    :returns: A string containing the default configuration.
    """
    if sys.version_info >= (3, 9):
        from importlib.resources import files
    else:
        from importlib_resources import files
    return files("grascii").joinpath(DEFAULTS_CONF_NAME).read_text()


def config_exists() -> bool:
    """Check whether the user configuration file exists.

    :returns: True if the configuration file exists.
    """

    return Path(get_config_file_path()).exists()


def get_config_file_path() -> PurePath:
    """Get a path object representing the location of the configuration
    file.

    :returns: A path object.
    """

    return PurePath(CONF_DIRECTORY, CONF_FILE_NAME)


def create_config() -> None:
    """Create a configuration file with the default settings."""

    Path(CONF_DIRECTORY).mkdir(parents=True, exist_ok=True)
    with Path(get_config_file_path()).open("w") as config:
        config.write(get_default_config())


def delete_config() -> None:
    """Delete a configuration file."""

    Path(get_config_file_path()).unlink()


def cli_config(args: argparse.Namespace) -> None:
    """Run a search using arguments parsed from the command line.

    :param args: A namespace of parsed arguments.
    """

    if args.where:
        if config_exists():
            print(get_config_file_path())
        else:
            print(
                "Configuration file does not exist. Use --init to create one.",
                file=sys.stderr,
            )
    elif args.init:
        if config_exists() and not args.force:
            print("Configuration file already exists.", file=sys.stderr)
            print(
                "If you would like to overwrite it with the default",
                "configuration, run again with --force.",
                file=sys.stderr,
            )
            return
        create_config()
        print("Configuration file created at", get_config_file_path())
    elif args.delete:
        if not config_exists():
            print("Configuration file does not exist.", file=sys.stderr)
            return
        if not args.force:
            print(
                "Are you sure you want to delete the configuration file?",
                "If so, run with --force.",
                file=sys.stderr,
            )
            return
        delete_config()
        print("Removed", get_config_file_path())


def main() -> None:
    """Run the config command using arguments from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_config(args)


if __name__ == "__main__":
    main()
