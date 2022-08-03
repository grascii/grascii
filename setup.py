#!/usr/bin/python

from __future__ import annotations

from setuptools import setup
from setuptools.command.build_py import build_py

from scripts.build_dictionaries import build_dictionaries
from scripts.create_grascii_regex import create_grascii_regex


class PreBuild(build_py):
    def run(self):
        build_dictionaries()
        create_grascii_regex()
        build_py.run(self)


setup(cmdclass={"build_py": PreBuild})
