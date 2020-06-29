
import unittest

from lark import Lark, Transformer, Token
from lark.visitors import CollapseAmbiguities

class PhraseFlattener(Transformer):
    def start(self, children):
        result = list()
        for child in children:
            for token in child:
                result.append(token)
        return result

    def short_to(self, children):
        token = type('',(object,),{"type": "TO"})()
        result = list()
        result.append(token)
        return result

    def __default__(self, data, children, meta):
        result = list()
        for child in children:
            if isinstance(child, Token):
                result.append(child)
            else:
                for token in child:
                    result.append(token)
        return result

class TestLessonPhrases(unittest.TestCase):

    # def __init__(self):
        # super.__init__(self)
        # self.parser = Lark.open("phrases.lark",
                # parser="earley")

    parser = Lark.open("phrases.lark",
            parser="earley")

    trans = PhraseFlattener()

    def _test_lesson(self, number):
        path = "./tests/phrasing/L" + str(number) + ".txt"
        with open(path, "r") as tests:
            for test in tests:
                phrase, expected = test.strip().split(maxsplit=1)
                with self.subTest(phrase=phrase, expected=expected):
                    tree = self.parser.parse(phrase)
                    tokens = self.trans.transform(tree)
                    tokens = (token.type for token in tokens)
                    parsed = " ".join(tokens)
                    self.assertEqual(parsed, expected)

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

if __name__ == '__main__':
    unittest.main()
