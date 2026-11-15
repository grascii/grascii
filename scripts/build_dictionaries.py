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
    builtins = [
        "preanniversary",
        "preanniversary-phrases",
        "anniversary",
        "anniversary-phrases",
    ]
    for name in builtins:
        builder.build(
            infiles=Path(f"dictionaries/builtins/{name}").glob("*.txt"),
            output=DictionaryOutputOptions(
                output_dir=Path(f"grascii/dictionary/{name}"),
            ),
        )


if __name__ == "__main__":
    build_dictionaries()
