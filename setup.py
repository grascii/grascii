#!/usr/bin/python

from pathlib import Path
from setuptools import setup
from setuptools.command.build_py import build_py

from grascii import dictionary

class CustomBuild(build_py):
    def run(self):
        print(Path("dsrc").glob("*.txt"))
        dictionary.build.build(infiles=Path("dsrc").glob("*.txt"),
                            output=Path("grascii/dictionary/preanniversary"),
                            package=True)
        build_py.run(self)


setup(
    setup_cfg=True,
    cmdclass={
        "build_py": CustomBuild
    }
)
