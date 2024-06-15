from __future__ import annotations

import logging
import unittest
from pathlib import Path

import pytest

from grascii.dictionary import Dictionary
from grascii.dictionary.build import (
    DEFAULT_PIPELINE,
    DictionaryBuilder,
    DictionaryOutputOptions,
)
from grascii.dictionary.common import (
    DictionaryAlreadyExists,
    DictionaryNotFound,
    get_dictionary_installed_name,
    get_dictionary_path_name,
)
from grascii.dictionary.install import install_dictionary
from grascii.dictionary.list import get_built_ins, get_installed
from grascii.dictionary.pipeline import create_grascii_check, create_spell_check
from grascii.dictionary.uninstall import uninstall_dictionary


class TestDictionaryBuildWarnings(unittest.TestCase):
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
            count_words=True,
        )
        summary = builder.build(
            infiles=[Path("tests/dictionaries/uncertainty.txt")],
            output=DictionaryOutputOptions(self.output_dir),
        )
        self.assertEqual(len(summary.warnings), 9)
        self.assertEqual(len(summary.errors), 0)
        for warning in summary.warnings:
            self.assertEqual(warning.level, logging.WARNING)
            self.assertRegex(warning.message, "Uncertainty")
        entry_count = sum(val for val in summary.entry_counts.values())
        self.assertEqual(entry_count, 9)

    def test_count(self):
        builder = DictionaryBuilder(
            count_words=True,
        )
        summary = builder.build(
            infiles=[Path("tests/dictionaries/count.txt")],
            output=DictionaryOutputOptions(self.output_dir),
        )
        self.assertEqual(len(summary.warnings), 10)
        self.assertEqual(len(summary.errors), 0)
        for warning in summary.warnings:
            self.assertEqual(warning.level, logging.WARNING)
            self.assertRegex(warning.message, "Too many")
        entry_count = sum(val for val in summary.entry_counts.values())
        self.assertEqual(entry_count, 12)

    def test_spelling(self):
        builder = DictionaryBuilder(
            pipeline=[
                *DEFAULT_PIPELINE,
                create_spell_check(
                    words_file=Path("tests/dictionaries/words.txt"),
                ),
            ],
            count_words=True,
        )
        summary = builder.build(
            infiles=[Path("tests/dictionaries/spell.txt")],
            output=DictionaryOutputOptions(self.output_dir),
        )
        self.assertEqual(len(summary.warnings), 5)
        self.assertEqual(len(summary.errors), 0)
        for warning in summary.warnings:
            self.assertEqual(warning.level, logging.WARNING)
            self.assertRegex(warning.message, "not in words")
        entry_count = sum(val for val in summary.entry_counts.values())
        self.assertEqual(entry_count, 9)

    def test_too_few_words(self):
        builder = DictionaryBuilder(
            count_words=True,
        )
        summary = builder.build(
            infiles=[Path("tests/dictionaries/too_few_words.txt")],
            output=DictionaryOutputOptions(self.output_dir),
        )
        self.assertEqual(len(summary.warnings), 0)
        self.assertEqual(len(summary.errors), 9)
        for error in summary.errors:
            self.assertEqual(error.level, logging.ERROR)
            self.assertRegex(error.message, "Too few")
        entry_count = sum(val for val in summary.entry_counts.values())
        self.assertEqual(entry_count, 0)

    def test_not_grascii(self):
        builder = DictionaryBuilder(
            pipeline=[*DEFAULT_PIPELINE, create_grascii_check()]
        )
        summary = builder.build(
            infiles=[Path("tests/dictionaries/not_grascii.txt")],
            output=DictionaryOutputOptions(self.output_dir),
        )
        self.assertEqual(len(summary.warnings), 0)
        self.assertEqual(len(summary.errors), 10)
        for error in summary.errors:
            self.assertEqual(error.level, logging.ERROR)
            self.assertRegex(error.message, "Failed to parse")
        entry_count = sum(val for val in summary.entry_counts.values())
        self.assertEqual(entry_count, 1)

    def test_comments_and_whitespace(self):
        builder = DictionaryBuilder()
        summary = builder.build(
            infiles=[Path("tests/dictionaries/comments.txt")],
            output=DictionaryOutputOptions(self.output_dir),
        )
        self.assertEqual(len(summary.warnings), 6)
        self.assertEqual(len(summary.errors), 0)
        for warning in summary.warnings:
            self.assertEqual(warning.level, logging.WARNING)
            self.assertRegex(warning.message, "Uncertainty")
        entry_count = sum(val for val in summary.entry_counts.values())
        self.assertEqual(entry_count, 7)


@pytest.mark.slow
class TestBuiltins(unittest.TestCase):
    def test_preanniversary(self):
        inputs = Path("dictionaries/builtins/preanniversary/").glob("*.txt")
        builder = DictionaryBuilder(
            count_words=True, pipeline=[*DEFAULT_PIPELINE, create_grascii_check()]
        )
        summary = builder.build(inputs, None)
        # Expecting one intentional error for "foyer"
        self.assertEqual(len(summary.errors), 1)


@pytest.fixture
def tmp_dict_path(tmp_path, monkeypatch):
    dict_path = tmp_path / "installed"
    dict_path.mkdir()
    monkeypatch.setattr("grascii.dictionary.INSTALLATION_DIR", dict_path)
    monkeypatch.setattr("grascii.dictionary.install.INSTALLATION_DIR", dict_path)
    monkeypatch.setattr("grascii.dictionary.uninstall.INSTALLATION_DIR", dict_path)
    monkeypatch.setattr("grascii.dictionary.list.INSTALLATION_DIR", dict_path)
    return dict_path


@pytest.fixture(scope="module")
def tmp_build_path(tmp_path_factory):
    build_path = tmp_path_factory.mktemp("search", numbered=False)
    builder = DictionaryBuilder()
    builder.build(
        infiles=Path("tests/dictionaries/search.txt"),
        output=DictionaryOutputOptions(build_path),
    )
    return build_path


class TestNewDictionary:
    def test_builtin(self):
        Dictionary.new(":preanniversary")

    def test_installed_does_not_exist(self):
        with pytest.raises(DictionaryNotFound):
            Dictionary.new(":unknown")

    def test_installed(self, tmp_dict_path, tmp_build_path):
        assert install_dictionary(tmp_build_path, tmp_dict_path) == ":search"
        Dictionary.new(":search")

    def test_path(self):
        Dictionary.new(Path("grascii/dictionary/preanniversary"))

    def test_string(self):
        Dictionary.new("grascii/dictionary/preanniversary")

    def test_path_does_not_exist(self):
        with pytest.raises(DictionaryNotFound):
            Dictionary.new(Path("unknown"))

    def test_string_does_not_exist(self):
        with pytest.raises(DictionaryNotFound):
            Dictionary.new("unknown")


class TestList:
    def test_list_no_installed(self, tmp_dict_path):
        assert len(get_installed()) == 0

    def test_list_builtins(self, tmp_dict_path):
        builtins = get_built_ins()
        assert len(builtins) == 1
        assert ":preanniversary" in builtins


class TestInstall:
    def test_install(self, tmp_dict_path, tmp_build_path):
        assert len(get_installed()) == 0
        assert install_dictionary(tmp_build_path, tmp_dict_path) == ":search"
        assert len(get_installed()) == 1
        assert ":search" in get_installed()

    def test_uninstall(self, tmp_dict_path, tmp_build_path):
        assert len(get_installed()) == 0
        assert install_dictionary(tmp_build_path, tmp_dict_path) == ":search"
        assert len(get_installed()) == 1
        uninstall_dictionary("search", tmp_dict_path)
        assert len(get_installed()) == 0

    def test_uninstall_nonexistent(self, tmp_dict_path):
        assert len(get_installed()) == 0
        with pytest.raises(DictionaryNotFound):
            uninstall_dictionary("search", tmp_dict_path)

    def test_install_name(self, tmp_dict_path, tmp_build_path):
        assert len(get_installed()) == 0
        assert install_dictionary(tmp_build_path, tmp_dict_path, name="two") == ":two"
        assert len(get_installed()) == 1
        assert ":two" in get_installed()

    def test_install_twice(self, tmp_dict_path, tmp_build_path):
        assert len(get_installed()) == 0
        assert install_dictionary(tmp_build_path, tmp_dict_path) == ":search"
        assert len(get_installed()) == 1
        with pytest.raises(DictionaryAlreadyExists):
            install_dictionary(tmp_build_path, tmp_dict_path)

    def test_install_force(self, tmp_dict_path, tmp_build_path):
        assert len(get_installed()) == 0
        assert install_dictionary(tmp_build_path, tmp_dict_path) == ":search"
        assert len(get_installed()) == 1
        with pytest.raises(DictionaryAlreadyExists):
            install_dictionary(tmp_build_path, tmp_dict_path)
        assert (
            install_dictionary(tmp_build_path, tmp_dict_path, force=True) == ":search"
        )


class TestCommon:
    def test_installed_name(self):
        assert get_dictionary_installed_name(":preanniversary") == ":preanniversary"
        assert get_dictionary_installed_name("preanniversary") == ":preanniversary"
        with pytest.raises(ValueError):
            get_dictionary_installed_name("")
        with pytest.raises(ValueError):
            get_dictionary_installed_name(":")

    def test_path_name(self):
        assert get_dictionary_path_name(":preanniversary") == "preanniversary"
        assert get_dictionary_path_name("preanniversary") == "preanniversary"
        with pytest.raises(ValueError):
            get_dictionary_path_name("")
        with pytest.raises(ValueError):
            get_dictionary_path_name(":")
