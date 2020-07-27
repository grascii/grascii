import io
from pkg_resources import resource_stream
from typing import TextIO

def get_words_file(name: str) -> TextIO:
    return io.TextIOWrapper(resource_stream("grascii.words", name),
            encoding="utf-8")
