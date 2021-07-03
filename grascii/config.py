"""Contains functions for working with a grascii configuration file.
Acts as the entry point for the grascii config command.

This can be invoked as a standalone program:
$ python -m grascii.config --help
"""

import argparse
from configparser import ConfigParser
from pathlib import Path, PurePath
from shutil import copyfile
import sys

SUPPORTS_INTERACTIVE = False
try:
    import questionary
    from questionary import Choice
    SUPPORTS_INTERACTIVE = True
except ImportError as e:
    pass

from grascii import regen
from grascii.appdirs import user_config_dir

APP_NAME = "grascii"
CONF_DIRECTORY = user_config_dir(APP_NAME)
CONF_FILE_NAME = APP_NAME + ".conf"

description = "Manage Grascii configuration"

def build_argparser(argparser: argparse.ArgumentParser) -> None: 
    """Configure an ArgumentParser parser to parse the config command-line
    options

    :parse argparser: A fresh ArgumentParser to configure.
    """

    group = argparser.add_mutually_exclusive_group(required=True)
    group.add_argument("--init", action="store_true",
            help="Create a configuration file.")
    group.add_argument("-D", "--delete", action="store_true",
            help="Delete an existing configuration file.")
    group.add_argument("-w", "--where", action="store_true",
            help="Print the path to the configuration file and exit.")
    argparser.add_argument("-f", "--force", action="store_true",
            help="Allow overwriting of an existing configuration file.")
    argparser.add_argument("-i", "--interactive", action="store_true",
            help="Run in interactive mode.")

def config_exists() -> bool:
    """Check whether the user configuration file exists.

    :returns: True if the configuration file exists.
    """

    return Path(get_config_file_path()).exists()

def get_config_file_path() -> PurePath:
    """Get a path object representating the location of the configuration
    file.

    :returns: A path object.
    """

    return PurePath(CONF_DIRECTORY, CONF_FILE_NAME)

def create_config() -> None:
    """Create a configuration file with the default settings."""

    Path(CONF_DIRECTORY).mkdir(parents=True, exist_ok=True)
    src = Path(__file__).with_name("defaults.conf")
    copyfile(src, get_config_file_path())

def interactive_edit_config() -> None:
    config = ConfigParser()
    # TODO: read as package resource
    config.read_file(Path(__file__).with_name("defaults.conf").open())
    config.read(get_config_file_path())

    questions = [
        {
            "type": "confirm",
            "name": "Search",
            "message": "Configure search?",
            "default": True,
            "auto_enter": False
        },
        {
            "type": "select",
            "name": "Uncertainty",
            "message": "Uncertainty",
            "choices": [str(i) for i in range(3)],
            "when": lambda x: x["Search"],
            "default": config["Search"].get("Uncertainty"),
        },
        {
            "type": "select",
            "name": "SearchMode",
            "message": "Search mode",
            "choices": [e.value for e in regen.SearchMode],
            "when": lambda x: x["Search"],
            "default": config["Search"].get("SearchMode"),
        },
        {
            "type": "select",
            "name": "AnnotationMode",
            "message": "Annotation mode",
            "choices": [e.value for e in regen.Strictness],
            "when": lambda x: x["Search"],
            "default": config["Search"].get("AnnotationMode"),
        },
        {
            "type": "select",
            "name": "AspirateMode",
            "message": "Aspirate mode",
            "choices": [e.value for e in regen.Strictness],
            "when": lambda x: x["Search"],
            "default": config["Search"].get("AspirateMode"),
        },
        {
            "type": "select",
            "name": "DisjoinerMode",
            "message": "Disjoiner mode",
            "choices": [e.value for e in regen.Strictness],
            "when": lambda x: x["Search"],
            "default": config["Search"].get("DisjoinerMode"),
        },
        {
            "type": "select",
            "name": "Interpretation",
            "message": "Interpretation",
            "choices": ["best", "all"],
            "when": lambda x: x["Search"],
            "default": config["Search"].get("Interpretation"),
        },
        {
            "type": "confirm",
            "name": "Build",
            "message": "Configure build?",
            "default": True,
            "auto_enter": False
        },
        {
            "type": "path",
            "name": "BuildDirectory",
            "message": "Build Output Directory",
            "when": lambda x: x["Build"],
            "default": config["Build"].get("BuildDirectory"),
        },

    ]

    print(questionary.prompt(questions))
    with open(get_config_file_path(), 'w') as config_file:
        config.write(config_file)



def delete_config() -> None:
    """Delete a configuration file."""

    Path(get_config_file_path()).unlink()


def cli_config(args: argparse.Namespace) -> None:
    """Run a search using arguments parsed from the command line.
    
    :param args: A namespace of parsed arguments.
    """

    if args.interactive:
        if not SUPPORTS_INTERACTIVE:
            print("The interactive extra is not installed", file=sys.stderr)
            return

    if args.where:
        if config_exists():
            print(get_config_file_path())
        else:
            print("Configuration file does not exist. Use --init to create one.", file=sys.stderr)
    elif args.init:
        if config_exists() and not args.force:
            if args.interactive:
                print("Configuration file already exists.")
                answer = questionary.confirm("Would you like to overwrite it?", default=False, auto_enter=False).ask()
                if not answer:
                    return
            else:
                print("Configuration file already exists.", file=sys.stderr)
                print("If you would like to overwrite it with the default",
                      "configuration, run again with --force or --interactive.", file=sys.stderr)
                return
        create_config()
        if args.interactive:
            interactive_edit_config()
        print("Configuration file created at", get_config_file_path())
    elif args.delete:
        if not config_exists():
            print("Configuration file does not exist.", file=sys.stderr)
            return
        if not args.force:
            if args.interactive:
                answer = questionary.confirm("Are you sure you want to delete the configuration file?", default=False, auto_enter=False).ask()
                if not answer:
                    return
            else:
                print("Are you sure you want to delete the configuration file?",
                      "If so, run with --force or --interactive.", file=sys.stderr)
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





