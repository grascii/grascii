
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


    def test_lesson1(self):
        path = "./tests/phrasing/L1.txt"
        with open(path, "r") as tests:
            for test in tests:
                phrase, expected = test.strip().split(maxsplit=1)
                with self.subTest(phrase=phrase):
                    tree = self.parser.parse(phrase)
                    tokens = self.trans.transform(tree)
                    tokens = (token.type for token in tokens)
                    parsed = " ".join(tokens)
                    self.assertEqual(parsed, expected)







if __name__ == '__main__':
    unittest.main()
