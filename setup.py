#!/usr/bin/python

import logging
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

from grascii import dictionary


class DictionaryBuild(build_py):
    def run(self):
        self._check_submodule()
        dictionary.build.build(
            infiles=Path("dictionaries/builtins/preanniversary").glob("*.txt"),
            output=Path("grascii/dictionary/preanniversary"),
            package=True,
        )
        build_py.run(self)

    def _check_submodule(self):
        if not Path("dictionaries/builtins").exists():
            logging.critical(
                "dictionaries/builtins does not exist. "
                + "Has the submodule been checked out?\n"
                + "Try: git submodule update --init"
            )
            raise RuntimeError("Missing dictionary build requirements")


setup(cmdclass={"build_py": DictionaryBuild})
