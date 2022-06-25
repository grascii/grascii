import unittest
from pathlib import Path
from shutil import rmtree

from grascii.dictionary.build import DictionaryBuilder
from grascii.searchers import GrasciiSearcher


class TestGrasciiSearcher(unittest.TestCase):

    output_dir = "tests/dictionaries/tosearch"

    @classmethod
    def setUpClass(cls):
        rmtree(cls.output_dir, ignore_errors=True)
        infiles = Path("tests/dictionaries/search.txt")
        builder = DictionaryBuilder(infiles=infiles, output=cls.output_dir)
        builder.build()

    @classmethod
    def tearDownClass(cls):
        rmtree(cls.output_dir, ignore_errors=True)

    def test_uncertainty(self):
        searcher = GrasciiSearcher(dictionaries=[self.output_dir])
        uncertainty_zero_result_count = len(
            searcher.search(grascii="FTH", uncertainty=0)
        )
        uncertainty_one_result_count = len(
            searcher.search(grascii="FTH", uncertainty=1)
        )
        uncertainty_two_result_count = len(
            searcher.search(grascii="FTH", uncertainty=2)
        )
        self.assertGreater(uncertainty_one_result_count, uncertainty_zero_result_count)
        self.assertGreater(uncertainty_two_result_count, uncertainty_one_result_count)

    def test_fix_first(self):
        searcher = GrasciiSearcher(dictionaries=[self.output_dir])
        fix_first_off_count = len(
            searcher.search(grascii="FTH", fix_first=False, uncertainty=1)
        )
        fix_first_on_count = len(
            searcher.search(grascii="FTH", fix_first=True, uncertainty=1)
        )
        self.assertGreater(fix_first_off_count, fix_first_on_count)

    def test_interpretation(self):
        searcher = GrasciiSearcher(dictionaries=[self.output_dir])
        best_interpretation_count = len(
            searcher.search(grascii="SSTN", interpretation="best", uncertainty=2)
        )
        all_interpretation_count = len(
            searcher.search(grascii="SSTN", interpretation="all", uncertainty=2)
        )
        self.assertGreater(all_interpretation_count, best_interpretation_count)

    def test_search_mode(self):
        searcher = GrasciiSearcher(dictionaries=[self.output_dir])
        match_count = len(searcher.search(grascii="ABT", search_mode="match"))
        start_count = len(searcher.search(grascii="ABT", search_mode="start"))
        contain_count = len(searcher.search(grascii="ABT", search_mode="contain"))
        self.assertGreater(start_count, match_count)
        self.assertGreater(contain_count, start_count)
