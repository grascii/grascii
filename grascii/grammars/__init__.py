"""Contains grammars used by grascii."""

from pathlib import Path


def get_grammar(name: str) -> str:
    """Get a grammar string.

    :param name: The name of the grammar resource.
    :returns: A grammar string.
    """

    return Path(__file__).with_name(name + ".lark")

    # return resource_string("grascii.grammars", name + ".lark").decode("utf-8")
