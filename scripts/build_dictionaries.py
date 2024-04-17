from __future__ import annotations

import logging
from pathlib import Path

from grascii import DictionaryBuilder, DictionaryOutputOptions


def check_submodule():
    if not Path("dictionaries/builtins").exists():
        logging.critical(
            "dictionaries/builtins does not exist. "
            + "Has the submodule been checked out?\n"
            + "Try: git submodule update --init"
        )
        raise RuntimeError("Missing dictionary build requirements")


def build_dictionaries():
    check_submodule()
    builder = DictionaryBuilder()
    builder.build(
        infiles=Path("dictionaries/builtins/preanniversary").glob("*.txt"),
        output=DictionaryOutputOptions(
            output_dir=Path("grascii/dictionary/preanniversary"),
            package=True,
        ),
    )


if __name__ == "__main__":
    build_dictionaries()
