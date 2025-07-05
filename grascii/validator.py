from __future__ import annotations

import re
from functools import lru_cache

from lark import Lark


@lru_cache(maxsize=1)
def get_grascii_regex_str() -> str:
    """Get a string that can be compiled into a regular expression that matches
    Grascii strings.
    """
    parser = Lark.open_from_package("grascii.grammars", "grascii_regex.lark")
    return parser.get_terminal("GRASCII").pattern.value


class GrasciiValidator:
    """Validates Grascii strings.

    :param ignore_case: Whether to ignore the case of the Grascii string. If
        ``False``, the Grascii string must be uppercase.
    :type ignore_case: bool
    """

    def __init__(self, ignore_case: bool = False) -> None:
        self._regex = re.compile(get_grascii_regex_str(), re.I if ignore_case else 0)

    def validate(self, grascii: str) -> bool:
        """Check whether the given string is valid Grascii.

        :param grascii: A string to check
        :returns: bool
        """
        return bool(self._regex.fullmatch(grascii))
