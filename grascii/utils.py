
import io
import os
from typing import Union, IO, TextIO
from warnings import warn

from pkg_resources import resource_stream, resource_string

def get_grammar(name: str) -> str:
    warn("This function is deprecated. Use grascii.grammars.get_grammar instead", DeprecationWarning)
    return resource_string("grascii.grammars", name + ".lark").decode("utf-8")

# def get_dict_file(dictionary: str, name: str) -> TextIO:
    # if dictionary[0] == ":":
        # if dictionary == ":preanniversary":
            # return io.TextIOWrapper(resource_stream("grascii.dict", name),
                    # encoding="utf-8")
    # return open(os.path.join(dictionary, name))

def get_words_file(name: str) -> TextIO:
    warn("This function is deprecated. Use grascii.words.get_words_file instead", DeprecationWarning)
    return io.TextIOWrapper(resource_stream("grascii.words", name),
            encoding="utf-8")


