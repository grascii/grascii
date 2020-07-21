#!/usr/bin/python

from setuptools import setup, find_packages

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
    }
)
