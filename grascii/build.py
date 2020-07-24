
import sys
import string
import argparse
import pathlib
import os
import time
from typing import TextIO, List, Optional, Union
from configparser import ConfigParser
from lark import Lark, UnexpectedInput

from grascii.utils import get_grammar

from grascii import defaults, grammar

description = "Build a Grascii Dictionary"

def build_argparser(argparser: argparse.ArgumentParser) -> None:
    argparser.add_argument("infiles", nargs="+", type=argparse.FileType("r"), 
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
        self.output = kwargs.get("output", "gdict")
        self.src_files = kwargs["infiles"]
        if kwargs.get("verbose", False):
            self.vprint = lambda *a, **k: None
        else:
            self.vprint = print

    def get_output_file(self, grascii: str) -> TextIO:
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
        print("W:", file_name + ":" + str(line_number), *message)
        print(line.strip())
        self.warnings += 1

    def log_error(self, file_name: str, line: str, line_number: int, *message: Union[str, List[str]]):
        print("E:", file_name + ":" + str(line_number), *message)
        print(line.strip())
        self.errors += 1

    def prepare_output_dir(self) -> None:
        if not self.check_only:
            self.out_dir = pathlib.Path(self.output)
            self.out_dir.mkdir(parents=True, exist_ok=True)
            if self.clean:
                for entry in self.out_dir.iterdir():
                    entry.unlink

        # premake out files?

    def load_parser(self) -> None:
        if self.parse:
            self.parser = Lark(get_grammar("grascii"), parser="earley", ambiguity="resolve")

    def load_word_set(self) -> None:
        if self.spell:
            self.words = set()

    def check_line(self, file_name: str, line: str, line_number: int) -> Optional[List[str]]:
        tokens = line.split()
        if tokens:
            if tokens[0][0] == "#":
                return None
            if tokens[0] == "?":
                self.log_warning(file_name, line, line_number, "Uncertainty")
                tokens.pop(0)
            if len(tokens) < 2:
                self.log_error(file_name, line, line_number, "Too few words")
                return None
            if len(tokens) > 2:
                self.log_warning(file_name, line, line_number, "Too many words")
                return None
        return tokens

    def check_grascii(self, grascii: str, file_name: str, line: str, line_number: int) -> bool:
        if self.parse:
            try:
                self.parser.parse(grascii)
            except UnexpectedInput:
                self.log_error(file_name, line, line_number, "Failed to parse", grascii)
                return False
        return True

    def check_word(self, word: str, file_name: str, line: str, line_number: int) -> bool:
        if self.spell:
            if word not in self.words:
                self.log_warning(file_name, line, line_number, word, "not in dictionary")
                return False
        return True

    def write_entry(self, grascii: str, word: str) -> None:
        if not self.check_only:
            out = self.get_output_file(grascii)
            out.write(grascii + " ")
            out.write(word + "\n")

    def close_output_files(self) -> None:
        for f in self.out_files.values():
            f.close()

    def print_build_summary(self, time: float) -> None:
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
        # time the build
        start_time = time.perf_counter() 

        self.load_word_set()
        self.load_parser()
        self.prepare_output_dir()

        try:
            for src_file in self.src_files:
                for i, line in enumerate(src_file):
                    tokens = self.check_line(src_file.name, line, i + 1)
                    if not tokens:
                        continue

                    grascii = tokens[0].upper()
                    # remove '-' characters
                    grascii = "".join(grascii.split("-"))
                    word = tokens[1].capitalize()

                    if not self.check_grascii(grascii, src_file.name, line, i + 1):
                        continue

                    if not self.check_word(word, src_file.name, line, i + 1):
                        continue
                   
                    self.write_entry(grascii, word)
        finally:
            self.close_output_files()

        end_time = time.perf_counter()
        self.print_build_summary(end_time - start_time)

def build(args):

    builder = DictionaryBuilder(**{k: v for k, v in vars(args).items() if v is not None})
    builder.build()
    return

    conf = ConfigParser()
    conf.read("grascii.conf")

    if args.output is None:
        args.output = conf.get('Build', 'BuildDirectory', 
                fallback=defaults.BUILD["BuildDirectory"])

    args.output = os.path.abspath(args.output)


    main_words_path = conf.get("Build", "MainWordList",
            fallback=defaults.BUILD["MainWordList"])

    supp_words_path = conf.get("Build", "SupplementaryWordList",
            fallback=defaults.BUILD["SupplementaryWordList"])

    en_dict = set()
    if args.spell:
        try:
            with open(main_words_path, "r") as words:
                en_dict |= set(line.strip().capitalize() for line in words)
        except FileNotFoundError:
            print("Could not find", main_words_path)
        try:
            with open(supp_words_path, "r") as words:
                en_dict |= set(line.strip().capitalize() for line in words)
        except FileNotFoundError:
            print("Could not find", supp_words_path)


def main(sys_args):
    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys_args)
    build(args)

if __name__ == "__main__":
    main(sys.argv[1:])

