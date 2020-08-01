#!/usr/bin/python

import argparse
from glob import glob
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

import grascii.build

class CustomBuild(build_py):
    def run(self):
        print(Path("dsrc").glob("*.txt"))
        grascii.build.build(infiles=Path("dsrc").glob("*.txt"),
                            output=Path("grascii/dict/preanniversary"),
                            package=True)
        build_py.run(self)


setup(
    name="grascii",
    version="0.1",
    packages=find_packages(exclude=["tests", "grascii.dict"]),
    package_data={
        "grascii": ["dict/*", "grammars/*.lark", "words/*.txt"]
    },
    install_requires=[
        "lark-parser>=0.8.6,!=0.8.7,!=0.8.8",
        "questionary>=1.5.1;python_version>='3.6'",
        "questionary<=1.4.0;python_version=='3.5'"
    ],
    # extras_require={
        # "interactive": ["questionary>=1.5.1"]
    # },
    entry_points={
        "console_scripts" : [
            "grascii = grascii.__main__:main"
        ]
    },
    cmdclass={
        "build_py": CustomBuild
    }
)
