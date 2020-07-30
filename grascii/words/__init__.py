"Contains word lists used for spell checking in dictionary building."

import io
from pkg_resources import resource_stream
from typing import TextIO

def get_words_file(name: str) -> TextIO:
    """Get a text stream of line separated words.
    
    :param name: The name of the word list to retrieve. (words.txt or 
        extra_words.txt)
    :returns: A text stream.
    """

    return io.TextIOWrapper(resource_stream("grascii.words", name),
            encoding="utf-8")
