import logging
import unittest
from pathlib import Path

from grascii.dictionary.build import DictionaryBuilder


class TestDictionaryBuildWarnings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.getLogger("grascii.dictionary.build").setLevel(logging.CRITICAL)

    output_dir = Path("tests/dictionaries/outputs")

    def setUp(self):
        self.output_dir.mkdir(exist_ok=True)
        for entry in self.output_dir.iterdir():
            entry.unlink()

    def tearDown(self):
        for entry in self.output_dir.iterdir():
            entry.unlink()
        self.output_dir.rmdir()

    def test_uncertainty(self):
        builder = DictionaryBuilder(
            infiles=[Path("tests/dictionaries/uncertainty.txt")],
            output=self.output_dir,
            count_words=True,
        )
        builder.build()
        self.assertEqual(len(builder.warnings), 9)
        self.assertEqual(len(builder.errors), 0)
        for warning in builder.warnings:
            self.assertEqual(warning.level, logging.WARNING)
            self.assertRegex(warning.message, "Uncertainty")
        entry_count = sum(val for val in builder.entry_counts.values())
        self.assertEqual(entry_count, 9)

    def test_count(self):
        builder = DictionaryBuilder(
            infiles=[Path("tests/dictionaries/count.txt")],
            output=self.output_dir,
            count_words=True,
        )
        builder.build()
        self.assertEqual(len(builder.warnings), 10)
        self.assertEqual(len(builder.errors), 0)
        for warning in builder.warnings:
            self.assertEqual(warning.level, logging.WARNING)
            self.assertRegex(warning.message, "Too many")
        entry_count = sum(val for val in builder.entry_counts.values())
        self.assertEqual(entry_count, 12)

    def test_spelling(self):
        builder = DictionaryBuilder(
            infiles=[Path("tests/dictionaries/spell.txt")],
            output=self.output_dir,
            count_words=True,
            words_file=Path("tests/dictionaries/words.txt"),
        )
        builder.build()
        self.assertEqual(len(builder.warnings), 5)
        self.assertEqual(len(builder.errors), 0)
        for warning in builder.warnings:
            self.assertEqual(warning.level, logging.WARNING)
            self.assertRegex(warning.message, "not in words")
        entry_count = sum(val for val in builder.entry_counts.values())
        self.assertEqual(entry_count, 9)

    def test_too_few_words(self):
        builder = DictionaryBuilder(
            infiles=[Path("tests/dictionaries/too_few_words.txt")],
            output=self.output_dir,
            count_words=True,
        )
        builder.build()
        self.assertEqual(len(builder.warnings), 0)
        self.assertEqual(len(builder.errors), 9)
        for error in builder.errors:
            self.assertEqual(error.level, logging.ERROR)
            self.assertRegex(error.message, "Too few")
        entry_count = sum(val for val in builder.entry_counts.values())
        self.assertEqual(entry_count, 0)

    def test_not_grascii(self):
        builder = DictionaryBuilder(
            infiles=[Path("tests/dictionaries/not_grascii.txt")],
            output=self.output_dir,
            parse=True,
        )
        builder.build()
        self.assertEqual(len(builder.warnings), 0)
        self.assertEqual(len(builder.errors), 10)
        for error in builder.errors:
            self.assertEqual(error.level, logging.ERROR)
            self.assertRegex(error.message, "Failed to parse")
        entry_count = sum(val for val in builder.entry_counts.values())
        self.assertEqual(entry_count, 1)

    def test_comments_and_whitespace(self):
        builder = DictionaryBuilder(
            infiles=[Path("tests/dictionaries/comments.txt")], output=self.output_dir
        )
        builder.build()
        self.assertEqual(len(builder.warnings), 6)
        self.assertEqual(len(builder.errors), 0)
        for warning in builder.warnings:
            self.assertEqual(warning.level, logging.WARNING)
            self.assertRegex(warning.message, "Uncertainty")
        entry_count = sum(val for val in builder.entry_counts.values())
        self.assertEqual(entry_count, 7)


class TestBuiltins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.getLogger("grascii.dictionary.build").setLevel(logging.CRITICAL)

    def test_preanniversary(self):
        inputs = Path("dictionaries/builtins/preanniversary/").glob("*.txt")
        builder = DictionaryBuilder(
            infiles=inputs, check_only=True, count_words=True, parse=True
        )
        builder.build()
        self.assertEqual(len(builder.errors), 0)
