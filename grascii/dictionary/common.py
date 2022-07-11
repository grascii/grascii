from __future__ import annotations


class DictionaryException(Exception):
    pass


class DictionaryAlreadyExists(DictionaryException):
    def __init__(self, name: str) -> None:
        self.name = name


class DictionaryNotFound(DictionaryException):
    def __init__(self, name: str) -> None:
        self.name = name


def get_dictionary_installed_name(name: str) -> str:
    if not name:
        raise ValueError("name cannot be the empty string")
    if name[0] == ":":
        if len(name) == 1:
            raise ValueError("name cannot be ':'")
        return name
    return ":" + name


def get_dictionary_path_name(name: str) -> str:
    if not name:
        raise ValueError("name cannot be the empty string")
    if name[0] == ":":
        if len(name) == 1:
            raise ValueError("name cannot be ':'")
        return name[1:]
    return name
