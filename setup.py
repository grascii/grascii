#!/usr/bin/python

import argparse
from glob import glob
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

import grascii.build_dict

class CustomBuild(build_py):
    def run(self):
        argparser = argparse.ArgumentParser()
        grascii.build_dict.build_argparser(argparser)
        args = argparser.parse_args(glob("./dsrc/*.txt") + ["--output=./grascii/dict"])
        grascii.build_dict.main(args)
        build_py.run(self)


setup(
    name="grascii",
    version="0.1",
    packages=find_packages(exclude=["tests"]),
    package_data={
        "" : ["dict/*"],
        "grascii.grammars": ["*.lark"]
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
