
from setuptools import setup, find_packages

setup(
    name="grascii",
    version="0.1",

    packages=find_packages(exclude=["tests"]),
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
