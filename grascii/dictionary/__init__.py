from __future__ import annotations

import argparse
import io
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Optional, TextIO, Union

from pkg_resources import resource_exists, resource_stream

from grascii.dictionary import build, install
from grascii.dictionary import list as list_dict
from grascii.dictionary import uninstall
from grascii.dictionary.common import INSTALLATION_DIR
from grascii.dictionary.install import install_dictionary  # noqa: F401
from grascii.dictionary.list import get_built_ins, get_installed  # noqa: F401
from grascii.dictionary.uninstall import uninstall_dictionary  # noqa: F401

if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files

description = "Create and manage Grascii dictionaries"


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    argparser.set_defaults(func=list_dict.cli_list)
    subparsers = argparser.add_subparsers(title="subcommands")

    build_parser = subparsers.add_parser(
        "build", description=build.description, help=build.description, aliases=["b"]
    )
    build.build_argparser(build_parser)
    build_parser.set_defaults(func=build.cli_build)

    install_parser = subparsers.add_parser(
        "install",
        description=install.description,
        help=install.description,
        aliases=["i"],
    )
    install.build_argparser(install_parser)
    install_parser.set_defaults(func=install.cli_install)

    uninstall_parser = subparsers.add_parser(
        "uninstall",
        description=uninstall.description,
        help=uninstall.description,
        aliases=["u"],
    )
    uninstall.build_argparser(uninstall_parser)
    uninstall_parser.set_defaults(func=uninstall.cli_uninstall)

    list_parser = subparsers.add_parser(
        "list",
        description=list_dict.description,
        help=list_dict.description,
        aliases=["l"],
    )
    list_dict.build_argparser(list_parser)
    list_parser.set_defaults(func=list_dict.cli_list)


class DictionaryNotFoundError(Exception):
    pass


BUILTIN_PACKAGE = "grascii.dictionary"


class DictionaryType(Enum):
    BUILTIN = 0
    INSTALLED = 1
    LOCAL = 2


class Dictionary:
    def __init__(
        self, path: os.PathLike, dtype: DictionaryType, name: Optional[str] = None
    ) -> None:
        self.path = path
        self.name = name if name is not None else path.name
        self.type = dtype

    def open(self, name: str) -> TextIO:
        return Path(self.path, name).open()

    @classmethod
    def new(cls, name: Union[str, os.PathLike]) -> Dictionary:
        if isinstance(name, str) and len(name) > 1 and name[0] == ":":
            installed_name = name[1:]
            dictionary_path = files(BUILTIN_PACKAGE).joinpath(installed_name)
            if dictionary_path.is_dir():
                return Dictionary(dictionary_path, DictionaryType.BUILTIN)
            dictionary_path = DICTIONARY_PATH / installed_name
            if dictionary_path.is_dir():
                return Dictionary(dictionary_path, DictionaryType.INSTALLED)
        dictionary_path = Path(name)
        if dictionary_path.is_dir():
            return Dictionary(dictionary_path, DictionaryType.LOCAL)
        raise DictionaryNotFoundError()


def get_dict_file(dictionary: str, name: str) -> TextIO:
    if dictionary[0] == ":":
        if resource_exists("grascii.dictionary", dictionary[1:]):
            module = "grascii.dictionary." + dictionary[1:]
            return io.TextIOWrapper(resource_stream(module, name), encoding="utf-8")
        directory = INSTALLATION_DIR.joinpath(dictionary[1:])
        if not directory.exists():
            print(dictionary, "does not exist.", file=sys.stderr)
        return directory.joinpath(name).open()
    return Path(dictionary, name).open()
