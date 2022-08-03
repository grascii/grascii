from __future__ import annotations

import logging
from pathlib import Path

from grascii import dictionary


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
    dictionary.build.build(
        infiles=Path("dictionaries/builtins/preanniversary").glob("*.txt"),
        output=Path("grascii/dictionary/preanniversary"),
        package=True,
    )


if __name__ == "__main__":
    build_dictionaries()
