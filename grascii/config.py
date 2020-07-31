
import argparse
from pathlib import Path, PurePath
from shutil import copyfile
import sys

from appdirs import user_config_dir

APP_NAME = "grascii"
CONF_DIRECTORY = user_config_dir(APP_NAME)
CONF_FILE_NAME = APP_NAME + ".conf"

description = "configure grascii"

def build_argparser(argparser: argparse.ArgumentParser) -> None: 
    argparser.add_argument("--init", action="store_true",
            help="Create a configuration file.")
    argparser.add_argument("-w", "--where", action="store_true",
            help="Print the path to the configuration file and exit.")
    argparser.add_argument("-f", "--force", action="store_true",
            help="Allow overwriting of an existing configuration file.")

def config_exists() -> bool:
    path = Path(CONF_DIRECTORY, CONF_FILE_NAME)
    return path.exists()

def main() -> None:
    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    if args.where:
        if config_exists():
            print(PurePath(CONF_DIRECTORY, CONF_FILE_NAME))
        else:
            print("Configuration file does not exist. Use --init to create one.")
    elif args.init:
        if config_exists() and not args.force:
            print("Configuration file already exists.")
            print("If you would like to overwrite it with the default", 
                  "configuration, run again with --force.")
            return
        dest = Path(CONF_DIRECTORY)
        dest.mkdir(parents=True, exist_ok=True)
        dest /= CONF_FILE_NAME
        src = Path(__file__).with_name("defaults.conf")
        copyfile(src, dest)
        print("Configuration file created at", dest)

if __name__ == "__main__":
    main()





