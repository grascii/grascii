#!/usr/bin/python

import argparse
from glob import glob
import os
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

import grascii.build_dict

class CustomBuild(build_py):
    def run(self):
        grascii.build_dict.main(glob(os.path.join("dsrc", "*.txt")) + 
            ["--output", os.path.join("grascii", "dict")])
        build_py.run(self)


setup(
    name="grascii",
    version="0.1",
    packages=find_packages(exclude=["tests", "grascii.dict"]),
    package_data={
        "grascii": ["dict/*", "grammars/*.lark"]
    },
    install_requires=[
        "lark-parser",
        "questionary"
    ],
    entry_points={
        "console_scripts" : [
            "grascii = grascii.__main__:main"
        ]
    },
    cmdclass={
        "build_py": CustomBuild
    }
)
