"""
Acts as the main entry point for the grascii build command and contains the
dictionary builder implementation.

This can be invoked as a standalone program:
$ python -m grascii.dictionary.build --help
"""

from __future__ import annotations

import argparse
import logging
import os
import pathlib
import re
import sys
import time
from contextlib import nullcontext
from dataclasses import dataclass
from fileinput import FileInput
from typing import Dict, Iterable, List, NamedTuple, Optional, TextIO, Tuple

from grascii import grammar
from grascii.dictionary.pipeline import (
    CancelPipeline,
    PipelineFunc,
    create_grascii_check,
    create_spell_check,
    remove_boundaries,
    standardize_case,
)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


description = "Build a Grascii Dictionary"


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    """Configure an ArgumentParser parser to parse the build command-line
    options.

    :param argparser: A fresh ArgumentParser to configure.
    """

    argparser.add_argument(
        "infiles", nargs="+", type=pathlib.Path, help="the files to process"
    )
    output_group = argparser.add_argument_group("output")
    exclusive_output_group = output_group.add_mutually_exclusive_group(required=True)
    exclusive_output_group.add_argument(
        "-o",
        "--output",
        type=os.path.abspath,
        help="path to a directory to output dictionary files",
    )
    exclusive_output_group.add_argument(
        "--no-output",
        action="store_true",
        help="do not output files and only perform validation",
    )
    output_group.add_argument(
        "-c",
        "--clean",
        action="store_true",
        help="clean the output directory before building",
    )
    validation_group = argparser.add_argument_group("validation")
    validation_group.add_argument(
        "-p",
        "--parse",
        action="store_true",
        help="enable syntax checking on grascii strings",
    )
    validation_group.add_argument(
        "-w",
        "--words",
        dest="words_file",
        type=pathlib.Path,
        help="path to a words file for spell checking",
    )
    validation_group.add_argument(
        "-n",
        "--count",
        dest="count_words",
        action="store_true",
        help="enable word count validation",
    )
    argparser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        action="count",
        default=0,
        help="increase output verbosity",
    )
    argparser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="suppress output",
    )


class NoMatchingOutputFile(Exception):
    pass


class BuildMessage(NamedTuple):
    file_name: str
    line: str
    line_number: int
    message: str
    level: int


class _BuilderLoggerAdapter(logging.LoggerAdapter):
    """A LoggerAdapter for dictionary builds that holds context on the current
    file and line being processed and maintains lists of BuildMessages
    for warnings and errors that occur during a build.
    """

    def __init__(self, logger: logging.Logger):
        super().__init__(logger, {})
        self._file_name: str = ""
        self._line: str = ""
        self._line_number: int = 0
        self.warnings: List[BuildMessage] = []
        self.errors: List[BuildMessage] = []

    def set_context(self, file_name: str, line: str, line_number: int):
        """Sets the context of the entry being processed.

        :param file_name: The name of the dictionary source file.
        :param line: The content of the line from the source file.
        :param line_number: The line number of ``line`` in the source file.
        """

        self._file_name = file_name
        self._line = line.strip()
        self._line_number = line_number

    def warning(self, msg, *args, **kwargs):
        message = f"{self._file_name}:{self._line_number} {msg}\n{self._line}"
        self.warnings.append(
            BuildMessage(
                self._file_name,
                self._line,
                self._line_number,
                message,
                logging.WARNING,
            )
        )
        self.logger.warning(message, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        message = f"{self._file_name}:{self._line_number} {msg}\n{self._line}"
        self.errors.append(
            BuildMessage(
                self._file_name,
                self._line,
                self._line_number,
                message,
                logging.ERROR,
            )
        )
        self.logger.error(message, *args, **kwargs)


@dataclass
class DictionaryOutputOptions:
    """Options for dictionary build output.

    :param output_dir: The directory where to output the dictionary files.
    :param clean: Whether to delete all files in the output directory before
        building.
    :param package: Whether to make the output directory a Python package by
        outputing an `__init__.py` file.
    :type output_dir: os.PathLike
    :type clean: bool
    :type package: bool
    """

    output_dir: os.PathLike
    clean: bool = False
    package: bool = False


class _OutputManager:
    def __init__(
        self,
        options: DictionaryOutputOptions,
        logger: logging.LoggerAdapter,
    ):
        self.options = options
        self._logger = logger
        self.entry_counts: Dict[str, int] = {}
        self._out_files: Dict[str, TextIO] = {}

    def __enter__(self):
        self._prepare_output_dir()
        return self._write_entry

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_output_files()

    def _prepare_output_dir(self) -> None:
        """Make and clean the output directory if necessary."""

        out_dir = pathlib.Path(self.options.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        if self.options.clean:
            self._logger.info("Cleaning output directory: %s", out_dir)
            for entry in out_dir.iterdir():
                entry.unlink()
        if self.options.package:
            self._logger.info("Creating __init__.py in %s", out_dir)
            out_dir.joinpath("__init__.py").touch()

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
            result = self._out_files[char]
            self.entry_counts[char] += 1
            return result
        except KeyError:
            out_file = pathlib.Path(self.options.output_dir, char)
            self._out_files[char] = out_file.open("w")
            self._logger.info("Opened output file: %s", out_file)
            self.entry_counts[char] = 1
            return self._out_files[char]

    def _write_entry(self, grascii: str, translation: str) -> None:
        """Write an entry to an output file.

        :param grascii: The grascii string to write.
        :param translation: The grascii string's corresponding translation to write.
        """

        out = self._get_output_file(grascii)
        out.write(grascii + " ")
        out.write(translation + "\n")

    def _close_output_files(self) -> None:
        """Close all output files."""

        for f in self._out_files.values():
            f.close()
        self._logger.info("Closed output files")


@dataclass
class BuildSummary:
    """Results of a dictionary build.

    :param time: The duration of the build in seconds.
    :param warnings: A list of warnings that occurred during the build.
    :param errors: A list of errors that occurred during the build.
    :param output_dir: The output directory of the dictionary.
    :param entry_counts: A dictionary of file names in the output directory to
        the number of entries written to that file.
    :type time: float
    :type warnings: List[BuildMessage]
    :type errors: List[BuildMessage]
    :type output_dir: Optional[os.PathLike]
    :type entry_counts: Optional[Dict[str, int]]
    """

    time: float
    warnings: List[BuildMessage]
    errors: List[BuildMessage]
    output_dir: Optional[os.PathLike]
    entry_counts: Optional[Dict[str, int]]

    def __str__(self):
        builder = []

        total = 0
        if self.entry_counts is not None:
            for key, val in self.entry_counts.items():
                total += val
                builder.append(
                    f"Wrote {val} entries to {os.path.join(self.output_dir, key)}"
                )
        if total > 0:
            builder.append("")

        builder.append(f"Finished Build in {self.time:.5f} seconds")
        if self.entry_counts is not None:
            builder.append(f"Entries: {total}")
        builder.append(f"Warnings: {len(self.warnings)}")
        builder.append(f"Errors: {len(self.errors)}")

        return "\n".join(builder)


DEFAULT_PIPELINE: List[PipelineFunc] = [remove_boundaries, standardize_case]
"""The default pipeline used for dictionary builds."""


class DictionaryBuilder:

    """A class that runs the build process for a grascii dictionary.

    :param parse: Whether to enable parse checking of grascii strings.
    :param words_file: A Path to a words file for spell checking
    :param count_words: Whether to enable word count validation.
    :param verbosity: Increase the output verbosity
    :param quiet: Suppress output
    :type parse: bool
    :type words_file: pathlib.Path
    :type count_words: bool
    :type verbosity: int
    :type quiet: bool
    """

    def __init__(self, **kwargs) -> None:
        self.pipeline: List[PipelineFunc] = kwargs.get("pipeline", DEFAULT_PIPELINE)
        self.count_words: bool = kwargs.get("count_words", False)
        self._logger = _BuilderLoggerAdapter(logger)
        quiet: bool = kwargs.get("quiet", False)
        verbosity: int = kwargs.get("verbosity", 0)
        self._set_logging_level(quiet, verbosity)

    def _set_logging_level(self, quiet: bool, verbosity: int):
        if quiet:
            logger.setLevel(logging.CRITICAL)
        else:
            levels = [logging.WARNING, logging.INFO, logging.DEBUG]
            verbosity = min(verbosity, len(levels))
            if verbosity > 0:
                logger.setLevel(levels[verbosity])

    def _parse_line(self, line: str) -> Optional[Tuple[str, str]]:
        """Parse a dictionary source file line into a Grascii string and its
        translation.

        :returns: A Grascii string and a translation or None if the line is a
            comment or contains an error."""

        tokens = line.split()
        if not tokens:
            return None

        if tokens[0][0] == "#":
            return None

        if tokens[0] == "?":
            self._logger.warning("Uncertainty")
            tokens = tokens[1:]

        match = re.match(r"\*(\d+)", tokens[0])
        count = 1
        if match:
            tokens = tokens[1:]
            assert match[1], match
            count = int(match[1])
        if len(tokens) < count + 1:
            self._logger.error(
                f"Too few words: Expected: {count} Got: {len(tokens) - 1}",
            )
            return None
        if count and len(tokens) > count + 1:
            if self.count_words:
                self._logger.warning(
                    f"Too many words: Expected: {count} Got: {len(tokens) - 1}"
                )

        return tokens[0], " ".join(tokens[1:])

    def build(
        self, infiles: Iterable[os.PathLike], output: Optional[DictionaryOutputOptions]
    ) -> BuildSummary:
        """Run the build based on the build settings given in the constructor.

        :param infiles: A collection of file paths to dictionary source files.
        :param output: Options for dictionary output.
        :type infiles: Iterable[os.PathLike]
        :type output: Optional[DictionaryOutputOptions]
        :returns: A BuildSummary
        """

        # reset warnings and errors
        self._logger = _BuilderLoggerAdapter(logger)

        # time the build
        start_time = time.perf_counter()

        self._logger.info("Starting build")

        if not output:
            self._logger.info(
                "Only checking source files. Output files will not be generated."
            )

        out = (
            _OutputManager(output, self._logger)
            if output
            else nullcontext(lambda x, y: None)
        )

        with out as write_entry:
            with FileInput(infiles) as f:
                for line in f:
                    self._logger.set_context(f.filename(), line, f.filelineno())
                    parsed = self._parse_line(line)
                    if not parsed:
                        continue
                    grascii, translation = parsed

                    try:
                        for func in self.pipeline:
                            grascii, translation = func(
                                grascii, translation, self._logger
                            )
                    except CancelPipeline:
                        self._logger.info(
                            "Pipeline aborted for {grascii}, {translation}"
                        )
                        continue

                    try:
                        write_entry(grascii, translation)
                    except NoMatchingOutputFile:
                        self._logger.error(
                            f"No output file for {grascii} {translation}"
                        )
                        continue

        end_time = time.perf_counter()
        total_time = end_time - start_time
        self._logger.info("Build completed in %s seconds", total_time)

        return BuildSummary(
            time=total_time,
            warnings=self._logger.warnings,
            errors=self._logger.errors,
            output_dir=output.output_dir if output else None,
            entry_counts=out.entry_counts if isinstance(out, _OutputManager) else None,
        )


def cli_build(args: argparse.Namespace) -> None:
    """Run a build using arguments parsed from the command line.

    :param args: A namespace of parsed arguments.
    """

    pipeline: List[PipelineFunc] = []
    pipeline.extend(DEFAULT_PIPELINE)
    if args.words_file:
        pipeline.append(create_spell_check(args.words_file))
    if args.parse:
        pipeline.append(create_grascii_check())

    builder = DictionaryBuilder(
        pipeline=pipeline,
        count_words=args.count_words,
        verbosity=args.verbosity,
        quiet=args.quiet,
    )
    output_options = (
        DictionaryOutputOptions(args.output, args.clean) if args.output else None
    )
    summary = builder.build(args.infiles, output_options)

    if not args.quiet:
        if summary.warnings or summary.errors:
            print()
        print(summary)


def main() -> None:
    """Run a build using arguments retrieved from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_build(args)


if __name__ == "__main__":
    main()
