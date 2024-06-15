from __future__ import annotations

from platformdirs import user_data_path

from grascii import APP_NAME

INSTALLATION_DIR = user_data_path(APP_NAME) / "dictionaries"

BUILTINS_PACKAGE = "grascii.dictionary"


class DictionaryException(Exception):
    """The base class for all dictionary-related exceptions."""

    pass


class DictionaryAlreadyExists(DictionaryException):
    def __init__(self, name: str) -> None:
        self.name = name


class DictionaryNotFound(DictionaryException):
    def __init__(self, name: str) -> None:
        self.name = name


def get_dictionary_installed_name(name: str) -> str:
    """Get the installed name of a dictionary.

    i.e. Prefixed with ':'
    """
    if not name:
        raise ValueError("name cannot be the empty string")
    if name[0] == ":":
        if len(name) == 1:
            raise ValueError("name cannot be ':'")
        return name
    return ":" + name


def get_dictionary_path_name(name: str) -> str:
    """Get the path name of a dictionary.

    i.e. Not prefixed with ':'
    """
    if not name:
        raise ValueError("name cannot be the empty string")
    if name[0] == ":":
        if len(name) == 1:
            raise ValueError("name cannot be ':'")
        return name[1:]
    return name


def is_dictionary_installed_name(name: str) -> bool:
    """Check whether the given name represents an installed dictionary."""
    return len(name) > 1 and name[0] == ":"
