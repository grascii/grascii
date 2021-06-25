#!/usr/bin/python

import argparse
from glob import glob
from pathlib import Path
from setuptools import setup, find_packages
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
    name="grascii",
    version="0.1.0.dev0",
    description="A language and tools to facilitate the study of Gregg Shorthand",
    author="Nicholas Chan",
    author_email="chanicpanic@gmail.com",
    url="https://github.com/chanicpanic/grascii",
    license="MIT",
    packages=find_packages(exclude=["tests", "grascii.dict"]),
    package_data={
        "grascii": ["dict/*", "grammars/*.lark", "words/*.txt"]
    },
    install_requires=[
        "lark-parser>=0.11.2",
    ],
    extras_require={
        "interactive": ["questionary>=1.5.1"],
    },
    entry_points={
        "console_scripts" : [
            "grascii = grascii.__main__:main"
        ]
    },
    cmdclass={
        "build_py": CustomBuild
    }
)
