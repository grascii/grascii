"""
Acts as the main entry point for the grascii build command and contains the
dictionary builder implementation.

This can be invoked as a standalone program:
$ python -m grascii.build --help
"""

import argparse
import logging
import os
import pathlib
import re
import sys
import time
from fileinput import FileInput
from typing import Dict, List, NamedTuple, Optional, Set, TextIO

from grascii import defaults, grammar

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

_VALIDATOR_AVAILABLE = False
try:
    from grascii.parser import GrasciiValidator

    _VALIDATOR_AVAILABLE = True
except ImportError:
    # Builds can still be run if Lark is not available
    logger.warning("Failed to import GrasciiValidator. Is lark installed?")


description = "Build a Grascii Dictionary"


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    """Configure an ArgumentParser parser to parse the build command-line
    options.

    :param argparser: A fresh ArgumentParser to configure.
    """

    argparser.add_argument(
        "infiles", nargs="+", type=pathlib.Path, help="the files to package"
    )
    argparser.add_argument(
        "-o",
        "--output",
        type=os.path.abspath,
        help="path to a directory to output dictionary files",
    )
    argparser.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="clean the output directory before building",
    )
    argparser.add_argument(
        "-p",
        "--parse",
        action="store_true",
        help="enable syntax checking on grascii strings",
    )
    argparser.add_argument(
        "-w",
        "--words",
        dest="words_file",
        type=pathlib.Path,
        help="path to a words file for spell checking",
    )
    argparser.add_argument(
        "-n",
        "--count",
        dest="count_words",
        action="store_true",
        help="enable word count validation",
    )
    argparser.add_argument(
        "-k",
        "--check-only",
        action="store_true",
        help="only check input; no output is generated",
    )
    argparser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
    )


class NoMatchingOutputFile(Exception):
    pass


class BuildMessage(NamedTuple):
    file_name: str
    line: str
    line_number: int
    message: str
    level: int


class DictionaryBuilder:

    """A class that runs the build process for a grascii dictionary.

    :param infiles: [Required] A list of files from which to generate the dictionary.
    :param clean: Whether to delete all files in the output directory before
        building.
    :param parse: Whether to enable parse checking of grascii strings.
    :param words_file: A Path to a words file for spell checking
    :param count_words: Whether to enable word count validation.
    :param check_only: Check source files without generating output.
    :param output: The directory where to output the dictionary files.
    :param verbosity: Increase the output verbosity
    :type infiles: Iterable[Union[Path, str]]
    :type clean: bool
    :type parse: bool
    :type words_file: pathlib.Path
    :type count_words: bool
    :type check_only: bool
    :type output: Union[Path, str]
    :type verbosity: int
    """

    def __init__(self, **kwargs) -> None:
        self.out_files: Dict[str, TextIO] = {}
        self.entry_counts: Dict[str, int] = {}
        self.warnings: List[BuildMessage] = []
        self.errors: List[BuildMessage] = []
        self.clean: bool = kwargs.get("clean", False)
        self.parse: bool = kwargs.get("parse", False)
        self.words_file: Optional[pathlib.Path] = kwargs.get("words_file")
        self.words: Set[str] = set()
        self.count_words: bool = kwargs.get("count_words", False)
        self.check_only: bool = kwargs.get("check_only", False)
        self.package: bool = kwargs.get("package", False)
        self.output: os.PathLike = kwargs.get(
            "output", defaults.BUILD["BuildDirectory"]
        )
        self.src_files: List[os.PathLike] = kwargs["infiles"]
        self.time: float = -1
        verbosity: int = kwargs.get("verbosity", 0)
        levels = [logging.WARNING, logging.INFO, logging.DEBUG]
        verbosity = min(verbosity, len(levels))
        if verbosity > 0:
            logger.setLevel(levels[verbosity])

    def _get_output_file(self, grascii: str) -> TextIO:
        """Get an output file corresponding to the first alphabetic characters
        in a grascii string.

        :param grascii: A grascii string to get an output file for.
        :returns: A text stream.
        """

        index = 0
        while index < len(grascii) and grascii[index] not in grammar.HARD_CHARACTERS:
            index += 1
        if index == len(grascii):
            raise NoMatchingOutputFile()

        char = grascii[index]
        try:
            result = self.out_files[char]
            self.entry_counts[char] += 1
            return result
        except KeyError:
            out_file = pathlib.Path(self.output, char)
            self.out_files[char] = out_file.open("w")
            logger.info("Opened output file: %s", out_file)
            self.entry_counts[char] = 1
            return self.out_files[char]

    def _log_warning(
        self, file_name: str, line: str, line_number: int, message: str
    ) -> None:
        """Print a build warning to stderr.

        :param file_name: The name of the dictionary source file that caused a
            warning.
        :param line: The line that generated the warning.
        :param line_number: The line number that generated the warning.
        :param message: A string to print
        """

        self.warnings.append(
            BuildMessage(file_name, line, line_number, message, logging.WARNING)
        )
        logger.warning(f"{file_name}:{line_number} {message}\n{line.strip()}")

    def _log_error(
        self, file_name: str, line: str, line_number: int, message: str
    ) -> None:
        """Print a build error to stderr.

        :param file_name: The name of the dictionary source file that caused a
            error.
        :param line: The line that generated the error.
        :param line_number: The line number that generated the error.
        :param message: A string to print
        """

        self.errors.append(
            BuildMessage(file_name, line, line_number, message, logging.ERROR)
        )
        logger.error(f"{file_name}:{line_number} {message}\n{line.strip()}")

    def _prepare_output_dir(self) -> None:
        """Make and clean the output directory if necessary."""

        if not self.check_only:
            out_dir = pathlib.Path(self.output)
            out_dir.mkdir(parents=True, exist_ok=True)
            if self.clean:
                logger.info("Cleaning output directory: %s", out_dir)
                for entry in out_dir.iterdir():
                    entry.unlink()
            if self.package:
                logger.info("Creating __init__.py in %s", out_dir)
                out_dir.joinpath("__init__.py").touch()

    def _load_parser(self) -> None:
        """Load a parser to check grascii strings."""

        if self.parse:
            if not _VALIDATOR_AVAILABLE:
                logger.warning("lark is unavailable. --parse will be ignored")
                return
            # Disable cache for now
            # It could be enabled, but we have to be careful about clearing the
            # cache after grammar changes
            self.parser = GrasciiValidator(use_cache=False)
            logger.info("Created GrasciiValidator")

    def _load_word_set(self) -> None:
        """Load a set of words to check the spelling of words."""

        if self.words_file:
            self.words = set()
            with self.words_file.open("r") as words:
                self.words |= set(line.strip().capitalize() for line in words)
            logger.info("Loaded words from %s", self.words_file)

    def _check_line(
        self, file_name: str, line: str, line_number: int
    ) -> Optional[List[str]]:
        """Check a dictionary source file line for comments, uncertainty,
        and incorrect token counts.

        :returns: A list of tokens from the line or None if the line contains
            an error."""

        tokens = line.split()
        if tokens:
            if tokens[0][0] == "#":
                return None
            if tokens[0] == "?":
                self._log_warning(file_name, line, line_number, "Uncertainty")
                tokens = tokens[1:]
            match = re.match(r"\*(\d+)", tokens[0])
            count = 1
            if match:
                tokens = tokens[1:]
                assert match[1], match
                count = int(match[1])
            if len(tokens) < count + 1:
                self._log_error(
                    file_name,
                    line,
                    line_number,
                    f"Too few words: Expected: {count} Got: {len(tokens) - 1}",
                )
                return None
            if count and len(tokens) > count + 1:
                if self.count_words:
                    self._log_warning(
                        file_name,
                        line,
                        line_number,
                        f"Too many words: Expected: {count} Got: {len(tokens) - 1}",
                    )
        return tokens

    def _check_grascii(
        self, grascii: str, file_name: str, line: str, line_number: int
    ) -> bool:
        """Check the parsabliity of a grascii string.

        :returns: False if parse checking is enabled and a parse fails.
        """

        if self.parse and _VALIDATOR_AVAILABLE:
            if not self.parser.validate(grascii):
                self._log_error(
                    file_name, line, line_number, f"Failed to parse {grascii}"
                )
                return False
        return True

    def _check_word(
        self, word: str, file_name: str, line: str, line_number: int
    ) -> bool:
        """Check the existence of a word in the word set.

        :returns: False if spell checking is enabled and the word does not
            exist in the word set.
        """

        if self.words:
            if word not in self.words:
                self._log_warning(
                    file_name, line, line_number, f"{word} not in words file"
                )
                return False
        return True

    def _write_entry(self, grascii: str, word: str) -> None:
        """Write an entry to an output file.

        :param grascii: The grascii string to write.
        :param word: The grascii string's corresponding word to write.
        """

        if not self.check_only:
            out = self._get_output_file(grascii)
            out.write(grascii + " ")
            out.write(word + "\n")

    def _close_output_files(self) -> None:
        """Close all output files."""

        for f in self.out_files.values():
            f.close()
        logger.info("Closed output files")

    def print_build_summary(self) -> None:
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
        formatted_time = f"{self.time:.5f}"
        print("Finished Build in", formatted_time, "seconds")
        if not self.check_only:
            print("Entries:", total)
        print("Warnings:", len(self.warnings))
        print("Errors:", len(self.errors))

    def build(self) -> None:
        """Run the build based on the build settings given in the constructor."""

        # time the build
        start_time = time.perf_counter()

        logger.info("Starting build")

        if self.check_only:
            logger.info(
                "Only checking source files. Output files will not be generated."
            )

        self._load_word_set()
        self._load_parser()
        self._prepare_output_dir()

        try:
            with FileInput(self.src_files) as f:
                for line in f:
                    tokens = self._check_line(f.filename(), line, f.filelineno())
                    if not tokens:
                        continue

                    grascii = tokens[0].upper()
                    # remove '-' characters
                    grascii = "".join(grascii.split("-"))
                    word_list = []
                    for word in tokens[1:]:
                        word_list.append(word.capitalize())
                        self._check_word(
                            word_list[-1], f.filename(), line, f.filelineno()
                        )
                    word = " ".join(word_list)

                    if not self._check_grascii(
                        grascii, f.filename(), line, f.filelineno()
                    ):
                        continue

                    try:
                        self._write_entry(grascii, word)
                    except NoMatchingOutputFile:
                        self._log_error(
                            f.filename(),
                            line,
                            f.filelineno(),
                            f"No output file for {grascii} {word}",
                        )
                        continue
        finally:
            self._close_output_files()

        end_time = time.perf_counter()
        self.time = end_time - start_time
        logger.info("Build completed in %s seconds", self.time)


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

    builder = DictionaryBuilder(
        **{k: v for k, v in vars(args).items() if v is not None}
    )
    builder.build()
    builder.print_build_summary()


def main() -> None:
    """Run a build using arguments retrieved from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_build(args)


if __name__ == "__main__":
    main()
