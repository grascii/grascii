from __future__ import annotations

import unittest
from pathlib import Path
from shutil import rmtree

from grascii.dictionary import DictionaryNotFound
from grascii.dictionary.build import DictionaryBuilder, DictionaryOutputOptions
from grascii.parser import InvalidGrascii
from grascii.searchers import GrasciiSearcher, RegexSearcher, ReverseSearcher

output_dir = "tests/dictionaries/tosearch"


def setUpModule():
    rmtree(output_dir, ignore_errors=True)
    infiles = [Path("tests/dictionaries/search.txt")]
    builder = DictionaryBuilder()
    builder.build(infiles=infiles, output=DictionaryOutputOptions(output_dir))


def tearDownModule():
    rmtree(output_dir, ignore_errors=True)


class TestGrasciiSearcher(unittest.TestCase):
    def test_uncertainty(self):
        searcher = GrasciiSearcher(dictionaries=[output_dir])
        uncertainty_zero_result_count = len(
            searcher.sorted_search(grascii="FTH", uncertainty=0)
        )
        uncertainty_one_result_count = len(
            searcher.sorted_search(grascii="FTH", uncertainty=1)
        )
        uncertainty_two_result_count = len(
            searcher.sorted_search(grascii="FTH", uncertainty=2)
        )
        self.assertGreater(uncertainty_one_result_count, uncertainty_zero_result_count)
        self.assertGreater(uncertainty_two_result_count, uncertainty_one_result_count)

    def test_fix_first(self):
        searcher = GrasciiSearcher(dictionaries=[output_dir])
        fix_first_off_count = len(
            searcher.sorted_search(grascii="FTH", fix_first=False, uncertainty=1)
        )
        fix_first_on_count = len(
            searcher.sorted_search(grascii="FTH", fix_first=True, uncertainty=1)
        )
        self.assertGreater(fix_first_off_count, fix_first_on_count)

    def test_interpretation(self):
        searcher = GrasciiSearcher(dictionaries=[output_dir])
        best_interpretation_count = len(
            searcher.sorted_search(grascii="SSTN", interpretation="best", uncertainty=2)
        )
        all_interpretation_count = len(
            searcher.sorted_search(grascii="SSTN", interpretation="all", uncertainty=2)
        )
        self.assertGreater(all_interpretation_count, best_interpretation_count)

    def test_search_mode(self):
        searcher = GrasciiSearcher(dictionaries=[output_dir])
        match_count = len(searcher.sorted_search(grascii="ABT", search_mode="match"))
        start_count = len(searcher.sorted_search(grascii="ABT", search_mode="start"))
        contain_count = len(
            searcher.sorted_search(grascii="ABT", search_mode="contain")
        )
        self.assertGreater(start_count, match_count)
        self.assertGreater(contain_count, start_count)

    def test_invalid_grascii(self):
        searcher = GrasciiSearcher(dictionaries=[output_dir])
        with self.assertRaises(InvalidGrascii):
            searcher.sorted_search(grascii="RAC")
        with self.assertRaises(InvalidGrascii):
            searcher.sorted_search(grascii="WAY")
        with self.assertRaises(InvalidGrascii):
            searcher.sorted_search(grascii="YES")

    def test_dictionary_not_found(self):
        with self.assertRaises(DictionaryNotFound):
            GrasciiSearcher(dictionaries=[":should-not-exist"])


class TestReverseSearcher(unittest.TestCase):
    def test_results(self):
        searcher = ReverseSearcher(dictionaries=[output_dir])
        result_count = len(searcher.sorted_search(reverse="habit"))
        self.assertEqual(result_count, 8)

    def test_no_grascii_match(self):
        searcher = ReverseSearcher(dictionaries=[output_dir])
        result_count = len(searcher.sorted_search(reverse="'ABT"))
        self.assertEqual(result_count, 0)

    def test_dictionary_not_found(self):
        with self.assertRaises(DictionaryNotFound):
            ReverseSearcher(dictionaries=["does-not-exist"])


class TestRegexSeacrher(unittest.TestCase):
    def test_dictionary_not_found(self):
        with self.assertRaises(DictionaryNotFound):
            RegexSearcher(dictionaries=[":preanniversary", ":cannot-exist"])
