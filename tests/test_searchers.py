from __future__ import annotations

import unittest
from pathlib import Path
from shutil import rmtree

from grascii.dictionary import DictionaryNotFound
from grascii.dictionary.build import DictionaryBuilder, DictionaryOutputOptions
from grascii.parser import InvalidGrascii
from grascii.searchers import GrasciiSearcher, RegexSearcher, ReverseSearcher

output_dir = "tests/dictionaries/tosearch"
sorted_output_dir = "test/dictionaries/sorted"


def build_dictionary(src, dest):
    rmtree(dest, ignore_errors=True)
    infiles = [Path(src)]
    builder = DictionaryBuilder()
    builder.build(infiles=infiles, output=DictionaryOutputOptions(dest))


def setUpModule():
    build_dictionary("tests/dictionaries/search.txt", output_dir)
    build_dictionary("tests/dictionaries/sort.txt", sorted_output_dir)


def tearDownModule():
    rmtree(output_dir, ignore_errors=True)
    rmtree(sorted_output_dir, ignore_errors=True)


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


class TestSortedGrasciiSearches(unittest.TestCase):
    def test_shorter_grascii_first(self):
        searcher = GrasciiSearcher(dictionaries=[sorted_output_dir])
        results = searcher.sorted_search(grascii="ABS", search_mode="start")
        self.assertListEqual(
            [r.entry.grascii for r in results],
            [
                "ABS",
                "ABSS",
                "ABSOL",
                "ABSTMUS",
            ],
        )

    def test_smaller_offset_match_first(self):
        searcher = GrasciiSearcher(dictionaries=[sorted_output_dir])
        results = searcher.sorted_search(grascii="MAS", search_mode="contain")
        self.assertListEqual(
            [r.entry.grascii for r in results],
            [
                "MAS",
                "AMAS",
                "PAMAS",
                "TASKMAS",
            ],
        )

    def test_better_matches_first(self):
        searcher = GrasciiSearcher(dictionaries=[sorted_output_dir])
        results = searcher.sorted_search(
            grascii="RELES", search_mode="contain", uncertainty=1
        )
        self.assertListEqual(
            [r.entry.grascii for r in results],
            [
                "RELES",
                "RELESB",
                "RELEZSH",
                "RELEF",
                "RELAPS",
                "RELAXSH",
                "RAREF",
            ],
        )

    def test_major_annotation_differences_appear_later(self):
        searcher = GrasciiSearcher(dictionaries=[sorted_output_dir])
        results = searcher.sorted_search(grascii="TAD", search_mode="contain")
        self.assertListEqual(
            [r.entry.grascii for r in results],
            [
                "STAD",
                "STADEM",
                "SETADL",
                "TA~DE|",
                "TA~DEN",
                "STA~D",
                "KUSTA~D",
                "DASTA~DE",
            ],
        )

    def test_minor_annotation_differences_special_handling(self):
        searcher = GrasciiSearcher(dictionaries=[sorted_output_dir])
        results = searcher.sorted_search(grascii="PO-E", search_mode="contain")
        self.assertListEqual(
            [r.entry.grascii for r in results],
            [
                "POES",
                "POESN",
                "POENANT",
                "POENANSE",
                "PO,EM",
                "PO,ESE",
                "PO,ETRE",
                "SPOEL",
                "SPOELR",
            ],
        )

    def test_exact_matches_appear_on_top(self):
        searcher = GrasciiSearcher(dictionaries=[sorted_output_dir])
        results = searcher.sorted_search(grascii="PO,E", search_mode="contain")
        self.assertListEqual(
            [r.entry.grascii for r in results],
            [
                "PO,EM",
                "PO,ESE",
                "PO,ETRE",
                "POES",
                "POESN",
                "POENANT",
                "POENANSE",
                "SPOEL",
                "SPOELR",
            ],
        )


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

    def test_regex_escape(self):
        searcher = ReverseSearcher(dictionaries=[output_dir])
        result_count = len(searcher.sorted_search(reverse="ag+.*"))
        self.assertEqual(result_count, 0)


class TestRegexSeacrher(unittest.TestCase):
    def test_dictionary_not_found(self):
        with self.assertRaises(DictionaryNotFound):
            RegexSearcher(dictionaries=[":preanniversary", ":cannot-exist"])
