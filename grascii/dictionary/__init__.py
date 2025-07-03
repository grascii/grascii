from __future__ import annotations

import argparse
import os
from enum import Enum
from importlib.resources import files
from pathlib import Path
from typing import Any, List, NamedTuple, Optional, TextIO, Union

from grascii.dictionary import build, install
from grascii.dictionary import list as list_dict
from grascii.dictionary import uninstall
from grascii.dictionary.common import (
    BUILTINS_PACKAGE,
    INSTALLATION_DIR,
    DictionaryNotFound,
    get_dictionary_installed_name,
    get_dictionary_path_name,
    is_dictionary_installed_name,
)
from grascii.dictionary.install import install_dictionary  # noqa: F401
from grascii.dictionary.list import get_built_ins, get_installed  # noqa: F401
from grascii.dictionary.uninstall import uninstall_dictionary  # noqa: F401
from grascii.grammar import HARD_CHARACTERS

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


class DictionaryEntry(NamedTuple):
    grascii: str
    translation: str


class DictionaryType(Enum):
    BUILTIN = 0
    INSTALLED = 1
    LOCAL = 2


class Dictionary:
    """
    A class that represents a grascii dictionary and provides methods for reading
    entries from the dictionary.
    """

    def __init__(
        self, path: os.PathLike, dtype: DictionaryType, name: Optional[str] = None
    ) -> None:
        self.path = path
        self.name = name if name is not None else path.name
        if dtype is DictionaryType.BUILTIN or dtype is DictionaryType.INSTALLED:
            self.name = get_dictionary_installed_name(self.name)
        self.type = dtype

    def open(self, name: str) -> TextIO:
        """Open a file from the dictionary with the given name for reading.
        The caller is responsible for closing the file.

        :param name: The name of the file to open.
        :type name: str

        :returns: A text stream.
        """
        return Path(self.path, name).open()

    def dump(self) -> List[DictionaryEntry]:
        """Get all the entries in this dictionary.

        :returns: A list of all entries in this dictionary.
        """
        entries = []

        for c in HARD_CHARACTERS:
            try:
                with self.open(c) as f:
                    for line in f:
                        grascii, translation = line.strip().split(maxsplit=1)
                        entries.append(DictionaryEntry(grascii, translation))
            except FileNotFoundError:
                continue

        return entries

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Dictionary) and self.path == other.path

    def __hash__(self) -> int:
        return hash(self.path)

    @classmethod
    def new(cls, name: Union[str, os.PathLike]) -> Dictionary:
        """Create a new dictionary from its installed name or a file path.

        :param name: The name of an installed dictionary (starting with ':') or \
                a path to a dictionary.
        :type name: Union[str, os.PathLike]

        :returns: A new Dictionary for the given name.
        """
        if isinstance(name, str) and is_dictionary_installed_name(name):
            path_name = get_dictionary_path_name(name)
            dictionary_path = files(BUILTINS_PACKAGE).joinpath(path_name)
            if dictionary_path.is_dir():
                return Dictionary(dictionary_path, DictionaryType.BUILTIN)
            dictionary_path = INSTALLATION_DIR / path_name
            if dictionary_path.is_dir():
                return Dictionary(dictionary_path, DictionaryType.INSTALLED)
        dictionary_path = Path(name)
        if dictionary_path.is_dir():
            return Dictionary(dictionary_path, DictionaryType.LOCAL)
        raise DictionaryNotFound(name)
