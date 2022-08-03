#!/usr/bin/python

from __future__ import annotations

import sys
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

sys.path.insert(0, str(Path(__file__).parent))

from scripts.build_dictionaries import build_dictionaries  # noqa: E402
from scripts.create_grascii_regex import create_grascii_regex  # noqa: E402


class PreBuild(build_py):
    def run(self):
        build_dictionaries()
        create_grascii_regex()
        build_py.run(self)


setup(cmdclass={"build_py": PreBuild})
