#!/usr/bin/python

from pathlib import Path
from setuptools import setup
from setuptools.command.build_py import build_py

from grascii import dictionary


class CustomBuild(build_py):
    def run(self):
        dictionary.build.build(
            infiles=Path("dictionaries/builtins/preanniversary").glob("*.txt"),
            output=Path("grascii/dictionary/preanniversary"),
            package=True,
        )
        build_py.run(self)


setup(cmdclass={"build_py": CustomBuild})
