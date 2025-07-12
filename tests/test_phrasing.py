from __future__ import annotations

import os
import unittest

import pytest
from lark import Lark

from grascii.dephrase import PhraseFlattener, dephrase
from grascii.lark_ambig_tools import CountedTree, Disambiguator


class TestLessonPhrases(unittest.TestCase):
    parser = Lark.open_from_package(
        "grascii.grammars",
        "phrases.lark",
        parser="earley",
        ambiguity="explicit",
        lexer="dynamic_complete",
        tree_class=CountedTree,
    )

    trans = PhraseFlattener()

    def _test_lesson(self, number):
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, "./phrasing/L" + str(number) + ".txt")
        with open(path, "r") as tests:
            for test in tests:
                phrase, expected = test.strip().split(maxsplit=1)
                with self.subTest(phrase=phrase, expected=expected):
                    trees = Disambiguator().visit(self.parser.parse(phrase))
                    tree = next(trees)
                    parsed_phrase = self._get_parsed_phrase(tree)
                    try:
                        self.assertEqual(parsed_phrase, expected)
                    except AssertionError:
                        passed = False
                        for parsed_phrase in map(self._get_parsed_phrase, trees):
                            if expected == parsed_phrase:
                                passed = True
                                break
                        if not passed:
                            self.fail(msg="failed ambiguity test")

    def _get_parsed_phrase(self, tree):
        tokens = self.trans.transform(tree)
        tokens = (token.type for token in tokens)
        return " ".join(tokens)

    def test_lesson1(self):
        self._test_lesson(1)

    def test_lesson2(self):
        self._test_lesson(2)

    def test_lesson3(self):
        self._test_lesson(3)

    def test_lesson4(self):
        self._test_lesson(4)

    def test_lesson5(self):
        self._test_lesson(5)

    def test_lesson6(self):
        self._test_lesson(6)

    def test_lesson7(self):
        self._test_lesson(7)

    def test_lesson11a(self):
        self._test_lesson("11a")

    def test_lesson11b(self):
        self._test_lesson("11b")

    def test_lesson11c(self):
        self._test_lesson("11c")

    def test_lesson11d(self):
        self._test_lesson("11d")

    def test_lesson11e(self):
        self._test_lesson("11e")

    @unittest.skip("fix these later")
    def test_lesson11f(self):
        self._test_lesson("11f")

    @unittest.skip("fix these later")
    def test_lesson11i(self):
        self._test_lesson("11i")

    @unittest.skip("fix these later")
    def test_lesson19a(self):
        self._test_lesson("19a")


@pytest.mark.slow
def test_aggressive():
    list(dephrase(phrase="thl-nbg", aggressive=True))
    list(dephrase(phrase="O(,^TH,TM", aggressive=True))


if __name__ == "__main__":
    unittest.main()
