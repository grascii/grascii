from __future__ import annotations

import os
import unittest

from lark import Lark
from lark.visitors import CollapseAmbiguities

from grascii.dephrase import PhraseFlattener, dephrase


class TestLessonPhrases(unittest.TestCase):
    parser = Lark.open_from_package(
        "grascii.grammars", "phrases.lark", parser="earley", ambiguity="resolve"
    )
    aparser = Lark.open_from_package(
        "grascii.grammars", "phrases.lark", parser="earley", ambiguity="explicit"
    )

    trans = PhraseFlattener()

    def _test_lesson(self, number):
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, "./phrasing/L" + str(number) + ".txt")
        with open(path, "r") as tests:
            for test in tests:
                phrase, expected = test.strip().split(maxsplit=1)
                with self.subTest(phrase=phrase, expected=expected):
                    tree = self.parser.parse(phrase)
                    tokens = self.trans.transform(tree)
                    tokens = (token.type for token in tokens)
                    parsed = " ".join(tokens)
                    try:
                        self.assertEqual(parsed, expected)
                    except AssertionError:
                        if not self.ambiguous_check(phrase, expected):
                            self.fail(msg="failed ambiguity test")

    def ambiguous_check(self, phrase, expected):
        tree = self.aparser.parse(phrase)
        trees = CollapseAmbiguities().transform(tree)
        trans = PhraseFlattener()
        parses = set()
        for t in trees:
            tokens = (token.type for token in trans.transform(t))
            parses.add(" ".join(tokens))
            # print(" ".join(tokens))

        return expected in parses

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

    @unittest.skip("fix these later")
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


def test_aggressive():
    dephrase(phrase="thl-nbg", aggressive=True)
    dephrase(phrase="O(,^TH,TM", aggressive=True)


if __name__ == "__main__":
    unittest.main()
