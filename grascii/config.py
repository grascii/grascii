"""Contains functions for working with a grascii configuration file.
Acts as the entry point for the grascii config command.

This can be invoked as a standalone program:
$ python -m grascii.config --help
"""

from __future__ import annotations

import argparse
import sys
from enum import Enum
from importlib.resources import files
from pathlib import Path, PurePath

from platformdirs import user_config_dir

from grascii import APP_NAME

CONF_DIRECTORY = user_config_dir(APP_NAME)
CONF_FILE_NAME = APP_NAME + ".conf"
DEFAULTS_CONF_NAME = "defaults.conf"

description = "Manage Grascii configuration"


class ConfigPreset(Enum):
    """An enum for the available config presets."""

    PREANNIVERSARY = "preanniversary"
    ANNIVERSARY = "anniversary"


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    """Configure an ArgumentParser parser to parse the config command-line
    options

    :parse argparser: A fresh ArgumentParser to configure.
    """

    argparser.set_defaults(func=lambda args: argparser.print_help())
    subparsers = argparser.add_subparsers(title="subcommands")

    init_description = "Create a configuration file"
    init_parser = subparsers.add_parser(
        "init",
        description=init_description,
        help=init_description,
    )
    init_parser.add_argument(
        "preset",
        action="store",
        choices=[preset.value for preset in ConfigPreset],
        help="The initial configuration to create",
    )
    init_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Allow overwriting of an existing configuration file",
    )
    init_parser.set_defaults(func=cli_init)

    delete_description = "Delete an existing configuration file"
    delete_parser = subparsers.add_parser(
        "delete",
        description=delete_description,
        help=delete_description,
    )
    delete_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Allow deleting an existing configuration file",
    )
    delete_parser.set_defaults(func=cli_delete)

    path_description = "Print the path to the configuration file and exit"
    path_parser = subparsers.add_parser(
        "path",
        description=path_description,
        help=path_description,
    )
    path_parser.set_defaults(func=cli_path)


def get_default_config() -> str:
    """Get the text of the default configuration file.

    :returns: A string containing the default configuration.
    """
    return files("grascii").joinpath(DEFAULTS_CONF_NAME).read_text()


def get_preset_config(preset: ConfigPreset):
    preset_config = get_default_config()
    if preset is ConfigPreset.ANNIVERSARY:
        preset_config = preset_config.replace(
            "Dictionary = :preanniversary :preanniversary-phrases",
            "Dictionary = :anniversary",
        )
    return preset_config


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


def create_config(preset: ConfigPreset) -> None:
    """Create a configuration file with preset settings.

    :param preset: The configuration to create.
    """

    Path(CONF_DIRECTORY).mkdir(parents=True, exist_ok=True)
    with Path(get_config_file_path()).open("w") as config:
        config.write(get_preset_config(preset))


def delete_config() -> None:
    """Delete a configuration file."""

    Path(get_config_file_path()).unlink()


def cli_init(args: argparse.Namespace) -> None:
    """Create a configuration file using arguments parsed from the command line.

    :param args: A namespace of parsed arguments.
    """
    if config_exists() and not args.force:
        print("Configuration file already exists.", file=sys.stderr)
        print(
            "If you would like to overwrite it with the specified preset",
            "configuration, run again with --force.",
            file=sys.stderr,
        )
        return
    create_config(ConfigPreset(args.preset))
    print("Configuration file created at", get_config_file_path())


def cli_delete(args: argparse.Namespace) -> None:
    """Delete a configuration file using arguments parsed from the command line.

    :param args: A namespace of parsed arguments.
    """
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


def cli_path(_: argparse.Namespace):
    """Print the path to the configuration file."""
    if config_exists():
        print(get_config_file_path())
    else:
        print(
            "Configuration file does not exist. Use init to create one.",
            file=sys.stderr,
        )


def main() -> None:
    """Run the config command using arguments from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    if args.func:
        args.func(args)
    else:
        argparser.print_help()


if __name__ == "__main__":
    main()
