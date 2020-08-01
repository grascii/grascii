"""
Acts as the main entry point for the grascii build command and contains the
dictionary builder implementation.

This can be invoked as a standalone program:
$ python -m grascii.build --help
"""

import argparse
import os
import pathlib
import re
import string
import sys
import time
from typing import TextIO, List, Optional, Union

from lark import Lark, UnexpectedInput

from grascii import defaults, grammar
from grascii.utils import get_grammar, get_words_file

description = "Build a Grascii Dictionary"

def build_argparser(argparser: argparse.ArgumentParser) -> None:
    """Configure an ArgumentParser parser to parse the build command-line
    options.
    
    :param argparser: A fresh ArgumentParser to configure.
    """

    argparser.add_argument("infiles", nargs="+", type=pathlib.Path,
            help="the files to package")
    argparser.add_argument("-o", "--output", type=os.path.abspath,
            help="path to a directory to output dictionary files")
    argparser.add_argument("-c", "--clean", action="store_true",
            help="clean the output directory before building")
    argparser.add_argument("-p", "--parse", action="store_true",
            help="enable syntax checking on grascii strings")
    argparser.add_argument("-s", "--spell", action="store_true",
            help="enable spell checking on english words")
    argparser.add_argument("-k", "--check-only", action="store_true",
            help="only check input; no output is generated")


class DictionaryBuilder():

    """A class that runs the build process for a grascii dictionary.

    :param infiles: [Required] A list of files from which to generate the dictionary.
    :param clean: Whether to delete all files in the output directory before
        building.
    :param parse: Whether to enable parse checking of grascii strings.
    :param spell: Whether to enable spell checking of words.
    :param check_only: Check source files without generating output.
    :param output: The directory where to output the dictionary files.
    :type infiles: Iterable[Union[Path, str]]
    :type clean: bool
    :type parse: bool
    :type spell: bool
    :type check_only: bool
    :type output: Union[Path, str]
    """

    def __init__(self, **kwargs):
        self.out_files = {}
        self.entry_counts = {}
        self.warnings = 0
        self.errors = 0
        self.clean = kwargs.get("clean", False)
        self.parse = kwargs.get("parse", False)
        self.spell = kwargs.get("spell", False)
        self.check_only = kwargs.get("check_only", False)
        self.package = kwargs.get("package", False)
        self.output = kwargs.get("output", defaults.BUILD["BuildDirectory"])
        self.src_files = kwargs["infiles"]
        if kwargs.get("verbose", False):
            self.vprint = lambda *a, **k: None
        else:
            self.vprint = print

    def get_output_file(self, grascii: str) -> TextIO:
        """Get an output file corresponding to the first alphabetic characters
        in a grascii string.
        
        :param grascii: A grascii string to get an output file for.
        :returns: A text stream.
        """

        index = 0
        while index < len(grascii) and grascii[index] not in grammar.HARD_CHARACTERS:
            index += 1
        if index == len(grascii):
            raise Exception()

        char = grascii[index]
        try:
            result = self.out_files[char]
            self.entry_counts[char] += 1
            return result
        except KeyError:
            self.out_files[char] = pathlib.Path(self.output, char).open("w")
            self.entry_counts[char] = 1
            return self.out_files[char]

    def log_warning(self, file_name: str, line: str, line_number: int, *message: Union[str, List[str]]) -> None:
        """Print a build warning to stderr.
        
        :param file_name: The name of the dictionary source file that caused a 
            warning.
        :param line: The line that generated the warning.
        :param line_number: The line number that generated the warning.
        :param message: A collection of strings to print as a message.
        """

        print("W:", file_name + ":" + str(line_number), *message, file=sys.stderr)
        print(line.strip(), file=sys.stderr)
        self.warnings += 1

    def log_error(self, file_name: str, line: str, line_number: int, *message: Union[str, List[str]]):
        """Print a build error to stderr.
        
        :param file_name: The name of the dictionary source file that caused a 
            error.
        :param line: The line that generated the error.
        :param line_number: The line number that generated the error.
        :param message: A collection of strings to print as a message.
        """
        
        print("E:", file_name + ":" + str(line_number), *message, file=sys.stderr)
        print(line.strip(), file=sys.stderr)
        self.errors += 1

    def prepare_output_dir(self) -> None:
        """Make and clean the output directory if necessary."""

        if not self.check_only:
            self.out_dir = pathlib.Path(self.output)
            self.out_dir.mkdir(parents=True, exist_ok=True)
            if self.clean:
                for entry in self.out_dir.iterdir():
                    entry.unlink
            if self.package:
                self.out_dir.joinpath("__init__.py").touch()

        # premake out files?

    def load_parser(self) -> None:
        """Load a parser to check grascii strings."""

        if self.parse:
            self.parser = Lark(get_grammar("grascii"), parser="earley", ambiguity="resolve")

    def load_word_set(self) -> None:
        """Load a set of words to check the spelling of words."""

        self.words = set()
        if self.spell:
            with get_words_file("words.txt") as words:
                    self.words |= set(line.strip().capitalize() for line in words)
            with get_words_file("extra_words.txt") as words:
                    self.words |= set(line.strip().capitalize() for line in words)

    def check_line(self, file_name: str, line: str, line_number: int) -> Optional[List[str]]:
        """Check a dictionary source file line for comments, uncertainty,
        and incorrect token counts.
        
        :returns: A list of tokens from the line or None if the line contains
            an error."""

        tokens = line.split()
        if tokens:
            if tokens[0][0] == "#":
                return None
            if tokens[0] == "?":
                self.log_warning(file_name, line, line_number, "Uncertainty")
                # tokens.pop(0)
                tokens = tokens[1:]
            if len(tokens) < 2:
                self.log_error(file_name, line, line_number, "Too few words")
                return None
            match = re.match(r"\*(\d*)", tokens[0])           
            count: Optional[int] = 1
            if match:
                tokens = tokens[1:]
                if match[1]:
                    count = int(match[1])
                else:
                    count = None
            if count and len(tokens) != count + 1:
                self.log_warning(file_name, line, line_number, 
                        "Incorrect number of words:",
                        "Expected:", str(count), "Got:", str(len(tokens) - 1))
                return None
        return tokens

    def check_grascii(self, grascii: str, file_name: str, line: str, line_number: int) -> bool:
        """Check the parsabliity of a grascii string.
        
        :returns: False if parse checking is enabled and a parse fails.
        """

        if self.parse:
            try:
                self.parser.parse(grascii)
            except UnexpectedInput:
                self.log_error(file_name, line, line_number, "Failed to parse", grascii)
                return False
        return True

    def check_word(self, word: str, file_name: str, line: str, line_number: int) -> bool:
        """Check the existence of a word in the word set.
        
        :returns: False if spell checking is enabled and the word does not
            exist in the word set.
        """

        if self.spell:
            if word not in self.words:
                self.log_warning(file_name, line, line_number, word, "not in dictionary")
                return False
        return True

    def write_entry(self, grascii: str, word: str) -> None:
        """Write an entry to an output file.
        
        :param grascii: The grascii string to write.
        :param word: The grascii string's corresponding word to write.
        """

        if not self.check_only:
            out = self.get_output_file(grascii)
            out.write(grascii + " ")
            out.write(word + "\n")

    def close_output_files(self) -> None:
        """Close all output files."""

        for f in self.out_files.values():
            f.close()

    def print_build_summary(self, time: float) -> None:
        """Print a summary of the build including warning, error, and entry counts
        as well as the time taken.
        
        :param time: The time in seconds taken to run the build.
        """

        if self.warnings or self.errors:
            print()
        total = 0
        for key, val in self.entry_counts.items():
            total += val
            print("Wrote", val, "entries to", os.path.join(self.output, key))
        if total > 0:
            print()
        formatted_time = "{:.5f}".format(time)
        print("Finished Build in", formatted_time, "seconds")
        if not self.check_only:
            print("Entries:", total)
        print("Warnings:", self.warnings)
        print("Errors:", self.errors)


    def build(self) -> None:
        """Run the build based on the build settings given in the constructor."""

        # time the build
        start_time = time.perf_counter() 

        self.load_word_set()
        self.load_parser()
        self.prepare_output_dir()

        try:
            for src_file in self.src_files:
                with open(src_file) as src_file:
                    for i, line in enumerate(src_file):
                        tokens = self.check_line(src_file.name, line, i + 1)
                        if not tokens:
                            continue

                        grascii = tokens[0].upper()
                        # remove '-' characters
                        grascii = "".join(grascii.split("-"))
                        # word = tokens[1].capitalize()
                        word = " ".join(t.capitalize() for t in tokens[1:])

                        if not self.check_grascii(grascii, src_file.name, line, i + 1):
                            continue

                        if not self.check_word(word, src_file.name, line, i + 1):
                            continue
                       
                        self.write_entry(grascii, word)
        finally:
            self.close_output_files()

        end_time = time.perf_counter()
        self.print_build_summary(end_time - start_time)

def build(**kwargs) -> None:
    """Run a dictionary build.

    For available arguments, see DictionaryBuilder.
    """

    builder = DictionaryBuilder(**kwargs)
    builder.build()

def cli_build(args: argparse.Namespace) -> None:
    """Run a build using arguments parsed from the command line.
    
    :param args: A namespace of parsed arguments.
    """

    build(**{k: v for k, v in vars(args).items() if v is not None})

def main() -> None:
    """Run a build using arguments retrieved from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_build(args)

if __name__ == "__main__":
    main()

